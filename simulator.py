import random

import statcollector as sc
import foosballgame

""" TODO: use foosballgame.FoosballMatchup
Class is used to simulate a matchup between two players

Potential overlap with matchup.Matchup

Note: 
- more information would be interesting
  -ex: max/min score for each player
       elo information
       probabilities for each potential outcome
- make it easy to change which games are used for calculations
  - need to change internal representation
"""
class Simulator:

    def __init__(self,matchup:foosballgame.FoosballMatchup): 
        # stat collector that includes all relevant games between player1 and player2
        self.stats = None
        self.attached = False

        # current status of the simulation
        self.matchup = matchup

    def set_game_to(self, val:int) -> bool:
        if not self.matchup.is_over():
            self.matchup.game_to = val
            return True
        return False

    def attach(self, stats:sc.StatCollector):
        if not self.attached:
            self.attached = True
            self.stats = stats

    def detach(self):
        self.attached = False
        self.stats = None

    """
    Resets the simulation with the option to chose the players
    """
    def reset_simulator(self, p1=None, p2=None):
        self.matchup.reset()
        if p1 is not None:
            self.matchup.home_team = p1
        if p2 is not None:
            self.matchup.away_team = p2

    def p1_score(self) -> int:
        return self.matchup.home_score
    
    def p2_score(self) -> int:
        return self.matchup.away_score
    
    def p1(self) -> str:
        return self.matchup.home_team
    
    def p2(self) -> str:
        return self.matchup.away_team
    
    def game_to(self) -> int:
        return self.matchup.game_to

    """
    Returns true if the game is over/ either player has self.game_to goals
    """
    def is_over(self) -> bool:
        return self.matchup.is_over()

    """
    Adds a goal to the given player's score
    """
    def add_goal(self,player:str) -> None:
        self.matchup.add_goal(player)

    """
    Get the total goals scored for player1 against player2 in all games
    """
    def get_goals_for(self, player:str) -> int:
        if player == self.p1():
            return self.stats.get_goals_scored_on(self.p1(),self.p2())
        elif player == self.p2():
            return self.stats.get_goals_scored_on(self.p2(),self.p1())
        else:
            return 0
        
    """
    Get the total wins for player1 against player2 in all games
    """
    def get_wins_for(self, player:str) -> int:
        if player == self.matchup.home_team:
            return self.stats.get_wins_against(self.matchup.home_team,self.matchup.away_team)
        elif player == self.matchup.away_team:
            return self.stats.get_wins_against(self.matchup.away_team,self.matchup.home_team)
        else:
            return 0 

    """
    The probability that player1 scores on player2 on a given point
    """
    def get_p1_goal_prob(self) -> float:
        raise RuntimeError('Not Implemented')

    """
    Simulates a singular goal using self.get_p1_goal_prob()
    """
    def simulate_goal(self) -> None:
        if not self.is_over():
            rand = random.random()
            if rand < self.get_p1_goal_prob():
                self.matchup.add_goal(self.matchup.home_team)
            else:
                self.matchup.add_goal(self.matchup.away_team)

    """
    Simulates the rest of the game from the current point to the end using self.simulate_goal()
    """
    def simulate_game(self) -> None:
        while not self.is_over():
            self.simulate_goal()

    """
    The probability that player1 wins against player2 given the current status of the simulation
    """
    def get_p1_win_odds(self) -> float:
        return foosballgame.get_win_prob(self.get_p1_goal_prob(),self.matchup.home_score,self.matchup.away_score,self.matchup.game_to)

    """
    Returns the expected score for the given player given the current status of the simulation
    """
    def get_expected_score(self,player:str) -> float:
        if player == self.matchup.home_team:
            goalprob = self.get_p1_goal_prob()
            pscore = self.matchup.home_score
            oppscore = self.matchup.away_score
        else:
            goalprob = 1-self.get_p1_goal_prob()
            pscore = self.matchup.away_score
            oppscore = self.matchup.home_score
        exp = 0
        for i in range(1,self.matchup.game_to+1):
            exp += i*foosballgame.get_prob_of_score(goalprob,i,pscore,oppscore,self.matchup.game_to)
        return exp
    
    """
    Return the probability that the given player gets the given score
    """
    def get_prob_of_score(self, player:str, score:int) -> float:
        if player == self.matchup.home_team:
            return foosballgame.get_prob_of_score(self.get_p1_goal_prob(),score,self.matchup.home_score,self.matchup.away_score,self.matchup.game_to)
        elif player == self.matchup.away_team:
            return foosballgame.get_prob_of_score(1-self.get_p1_goal_prob(),score,self.matchup.away_score,self.matchup.home_score,self.matchup.game_to)
        else:
            if score == 0:
                return 1
            else:
                return 0
            
    """
    Get the number of times a player scored score goals against the other player
    """
    def get_times_scored_n(self, player:str, score:int) -> int:
        if player == self.matchup.home_team:
            return self.stats.get_times_scored_n(self.matchup.home_team, self.matchup.away_team, score)
        elif player == self.matchup.away_team:
            return self.stats.get_times_scored_n(self.matchup.away_team, self.matchup.home_team, score)
        else:
            return 0

    """
    Returns the most probable score for te given player given the current status of the simulation
    """
    def get_most_probable_score(self, player:str) -> int:
        max_prob = 0
        score = 0
        for i in range(self.matchup.game_to):
            prob1 = foosballgame.get_prob_of_score(self.get_p1_goal_prob(),i,self.matchup.home_score,self.matchup.away_score,self.matchup.game_to)
            prob2 = foosballgame.get_prob_of_score(1-self.get_p1_goal_prob(),i,self.matchup.away_score,self.matchup.home_score,self.matchup.game_to)
            if prob1 > max_prob and prob1 > prob2:
                max_prob = prob1
                if player == self.matchup.home_team:
                    score = i
                else:
                    score = self.matchup.game_to
            if prob2 > max_prob:
                max_prob = prob2
                if player == self.matchup.home_team:
                    score = self.matchup.game_to
                else:
                    score = i
        return score
    
class SkillSimulator(Simulator):

    def __init__(self,matchup:foosballgame.FoosballMatchup):
        super().__init__(matchup)

    def get_p1_goal_prob(self) -> float:
        p1_skill = self.stats.skill_tracker.get_rating(self.matchup.home_team)
        p2_skill = self.stats.skill_tracker.get_rating(self.matchup.away_team)
        return p1_skill/(p1_skill+p2_skill)

class ProbabilitySimulator(Simulator):

    def __init__(self,matchup:foosballgame.FoosballMatchup):
        super().__init__(matchup)

    def get_p1_goal_prob(self) -> float:
        p1_goals = self.stats.get_goals_scored_on(self.matchup.home_team,self.matchup.away_team)
        p2_goals = self.stats.get_goals_scored_on(self.matchup.away_team,self.matchup.home_team)
        return (p1_goals+self.matchup.home_score+1)/(p1_goals+p2_goals+self.matchup.home_score+self.matchup.away_score+2)
    
def get_simulator(p1:str,p2:str,type:str):
    if type.lower() == 'skill':
        return SkillSimulator(foosballgame.FoosballMatchup(p1,p2,0))
    if type.lower() in ['prob', 'probability']:
        return ProbabilitySimulator(foosballgame.FoosballMatchup(p1,p2,0))
    else:
        print(f"Unknown simulator type {type}")
