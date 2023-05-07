import foosballgame

import pandas as pd

"""
This class calculates and stores elo ratings for players across foosball games

Notes: 
- doesn't account for possibility of ties: limited extensibility, easy fix if needed
- static k: would be interesting to have potential variablility in k
"""
class ELO_Calculator():
    
    """
    Pass in an initial rating for all players and a k value for all players
    Typical choices are 1500 for initial rating and 32 for k
    k can vary from game to game, when masters play k is typically 16
    Choosing k can determine how important a game is/ add a weigting
    """
    def __init__(self, initial_rating:int = 1500, k_value:int = 32) -> None:
        self.initial_rating = initial_rating
        self.k = k_value
        self.game_ratings = {}
        self.goal_ratings = {}

    """
    Return a dataframe that can be used by statcollector
    """
    def to_df(self):
        ratings = {}
        for player in self.game_ratings:
            ratings[player] = {'Name': player, 'ELO': self.get_game_elo(player), 'GOAL ELO': self.get_goal_elo(player)}
        return pd.DataFrame.from_dict(ratings,orient='index')

    """
    Add games to the ELO ranking and adjust the ratings according to the results
    """
    def add_games(self, games:list[foosballgame.FoosballGame]) -> None:
        for game in games:
            self.add_game(game)

    """
    Add a game to the ELO ranking and adjust the ratings according to the results
    """
    def add_game(self, game:foosballgame.FoosballGame) -> None:
        # make sure both players are included in the game_ratings
        if game.winner not in self.game_ratings:
            self.game_ratings[game.winner] = self.initial_rating
        if game.loser not in self.game_ratings:
            self.game_ratings[game.loser] = self.initial_rating

        # make sure both players are included in the goal_ratings
        if game.winner not in self.goal_ratings:
            self.goal_ratings[game.winner] = self.initial_rating
        if game.loser not in self.goal_ratings:
            self.goal_ratings[game.loser] = self.initial_rating

        # calculate each player's probability of winning a game
        winner_game_exp = self.get_win_probability(game.winner, game.loser)
        loser_game_exp  = 1-winner_game_exp # exp always adds to 1

        # update the ELO of each player based on their ratings, k, and the game result
        self.__update_game_elo(game.winner, 1, winner_game_exp)
        self.__update_game_elo(game.loser, 0, loser_game_exp)

        # calculate each player's probability of scoring a goal
        winner_goal_exp = self.get_goal_probability(game.winner, game.loser)
        loser_goal_exp  = 1-winner_goal_exp # exp always adds to 1

        # update the ELO of each player based on their ratings, k, and the game result
        winner_actual = (game.winner_score)/(game.winner_score + game.loser_score)
        loser_actual  = 1-winner_actual
        self.__update_goal_elo(game.winner, winner_actual, winner_goal_exp)
        self.__update_goal_elo(game.loser,  loser_actual,  loser_goal_exp)


    """
    Update the game elo of a player given the outcome of a game
    """
    def __update_game_elo(self, player:str, outcome:float, expected:float) -> None:
        self.game_ratings[player] += self.k*(outcome-expected)

    """
    Update the goal elo of a player given the outcome of a game
    """
    def __update_goal_elo(self, player, outcome:float, expected:float) -> None:
        self.goal_ratings[player] += self.k*(outcome-expected)

    """
    Calculate the expected probability that player1 beats player2
    """
    def get_win_probability(self, player1:str, player2:str) -> float:
        p1_odds = 1/(1+pow(10,(self.game_ratings[player2]-self.game_ratings[player1])/400))
        return p1_odds
    
    """
    Calculate the expected probability that player1 scores on player2
    """
    def get_goal_probability(self, player1:str, player2:str) -> float:
        p1_odds = 1/(1+pow(10,(self.goal_ratings[player2]-self.goal_ratings[player1])/400))
        return p1_odds

    """
    Get the game elo of a player
    """
    def get_game_elo(self, player:str) -> int:
        if player not in self.game_ratings:
            return self.initial_rating
        return int(self.game_ratings[player])
    
    """
    Get the goal elo of a player
    """
    def get_goal_elo(self, player:str) -> int:
        if player not in self.goal_ratings:
            return self.initial_rating
        return int(self.goal_ratings[player])
