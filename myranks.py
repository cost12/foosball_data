import math
import pandas as pd

import foosballgame

class PlayerSkill:

    def __init__(self, name:str):
        self.name = name

        self.skill = 0.5
        self.consistency = 0

        self.learning_rate_skill = 0
        self.learning_rate_consistency = 0

class RatingSystem:

    def __init__(self, name, learning_rate:float=0.1) -> None:
        self.name = name
        self.learning_rate = learning_rate
        self.players = dict[str,PlayerSkill]()

    def add_games(self, games:foosballgame.FoosballGame) -> None:
        for game in games:
            self.add_game(game)

    def add_game(self, game:foosballgame.FoosballGame) -> None:
        if game.winner not in self.players:
            self.players[game.winner] = PlayerSkill(game.winner)
        if game.loser not in self.players:
            self.players[game.loser] = PlayerSkill(game.loser)
        self.adjust_ratings(game)
    
    def adjust_ratings(self, game:foosballgame.FoosballGame):
        raise RuntimeError("Not Implemented")
    
    def get_game_rating(self, game, w_skill, l_skill) -> tuple[float]:
        raise RuntimeError("Not Implemented")
    
    def __get_score_rating(self, game:foosballgame.FoosballGame) -> tuple[float]:
        raise RuntimeError("Not Implemented")
    
    def normalize(self, ranks):
        raise RuntimeError("Not Implemented")
    
    def normalize_ind(self, rank):
        raise RuntimeError("Not Implemented")

    def get_ratings(self) -> list[PlayerSkill]:
        lis = list[PlayerSkill]()
        for player in self.players:
            lis.append(self.players[player])
        return self.normalize(lis)
    
    def get_rating(self, player) -> float:
        #new = PlayerSkill(player)
        #new.skill = self.normalize_ind(self.players[player].skill)
        #return new
        if player in self.players:
            return self.normalize_ind(self.players[player].skill)
        else:
            return self.normalize_ind(0.5)
    
    def to_df(self):
        ratings = {}
        for player in self.players:
            ratings[player] = {'Name': player, self.name: self.get_rating(player)}
        return pd.DataFrame.from_dict(ratings,orient='index')

    
class SimpleRating(RatingSystem):

    def __init__(self, name, learning_rate=0.1):
        super().__init__(name, learning_rate)

    def adjust_ratings(self, game:foosballgame.FoosballGame):
        w_rat, l_rat = self.get_game_rating(game,self.players[game.winner].skill,self.players[game.loser].skill) 
        self.players[game.winner].skill = self.learning_rate*w_rat+(1-self.learning_rate)*self.players[game.winner].skill
        self.players[game.loser].skill =  self.learning_rate*l_rat+(1-self.learning_rate)*self.players[game.loser].skill

    """
    Simple calculation for a game rating
    """
    def get_game_rating(self, game, w_skill, l_skill) -> tuple[float]:
        w_rat, l_rat = self.__get_score_rating(game)
        return math.sqrt(w_rat*l_skill), math.sqrt(l_rat*w_skill)
    
    """
    Returns the score rating for the winner and loser
    1 points for a shutout
    0.5 points would be a tie if possible
    0 points for not scoring
    Scores move linearly (jumps of 0.05 per goal for games to 10)
    """
    def __get_score_rating(self, game:foosballgame.FoosballGame) -> tuple[float]:
        goal_jump = 1/(2*game.winner_score)
        return 1-goal_jump*game.loser_score, goal_jump*game.loser_score
    
    def normalize(self, ranks, player = None):
        pass

    def normalize_ind(self, rank):
        pass
    

class SkillRating(RatingSystem):

    def __init__(self, name, learning_rate=0.1):
        super().__init__(name, learning_rate)

    def adjust_ratings(self, game:foosballgame.FoosballGame):
        w_rat, l_rat = self.get_game_rating(game,self.players[game.winner].skill,self.players[game.loser].skill) 
        self.players[game.winner].skill = self.learning_rate*w_rat+(1-self.learning_rate)*self.players[game.winner].skill
        self.players[game.loser].skill  = self.learning_rate*l_rat+(1-self.learning_rate)*self.players[game.loser].skill

    def get_game_rating(self, game, w_skill, l_skill) -> tuple[float]:
        w_rat, l_rat = self.__get_score_rating(game)
        return w_rat*(w_skill+l_skill), l_rat*(w_skill+l_skill)
    
    def __get_score_rating(self, game:foosballgame.FoosballGame) -> tuple[float]:
        win = game.winner_score / (game.winner_score + game.loser_score)
        return win, 1-win
    
    def normalize(self, ranks:list[PlayerSkill]) -> list[PlayerSkill]:
        div = self.__max_rat()/0.999
        new_lis = []
        for player in ranks:
            new_lis.append(PlayerSkill(player.name))
            new_lis[-1].skill = player.skill / div
        return new_lis
    
    def normalize_ind(self, rank):
        div = self.__max_rat()/0.999
        return rank/div
    
    def __max_rat(self):
        #return 1
        max = None
        for player in self.players:
            if max is None or self.players[player].skill > max:
                max = self.players[player].skill
        return max
    

def sort_rankings(rankings:list[PlayerSkill]) -> list[PlayerSkill]:
    rankings.sort(key=lambda x: x.skill, reverse=True)
    return rankings

def print_rankings(rankings:list[PlayerSkill]) -> None:
    for rank in rankings:
        print("{:<10} {:>.3f}".format(rank.name,rank.skill))

"""
Returns the rankings formatted for graph output
"""
def get_rankings_list(games:list[foosballgame.FoosballGame], xlist:list, players:list[str], is_daily:bool, syst=SkillRating, name:str='Skill', alpha:float=0.5) -> dict[str:float]:
    rankings = {}
    system = syst(name,alpha)
    game_ind = 0
    
    for player in players:
        rankings[player] = []
        
    for x in xlist:
        while game_ind < len(games) and ((is_daily and games[game_ind].date <= x) or ((not is_daily) and games[game_ind].number <= x)):
            system.add_game(games[game_ind])
            game_ind += 1
        for player in players:
            if player in system.players:
                rankings[player].append(system.get_rating(player))
            else:
                rankings[player].append(0)
    return rankings





















import random
import datetime

import data_read_in

def test() -> None:
    games = data_read_in.read_in_games_from_sheets()

    rating_system = SkillRating(learning_rate=0.1)
    rating_system.add_games(games)
    rating_system.normalize()
    print_rankings(sort_rankings(rating_system.get_ratings()))

if __name__=='__main__':
    test()