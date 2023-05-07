import random

#import statcollector as sc
import foosballgame

"""
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

    def __init__(self,p1:str,p2:str,stats): #:sc.StatCollector): TODO: figure out how to type hint here
        # the players being simulated
        self.player1 = p1
        self.player2 = p2

        # stat collector that includes all relevant games between player1 and player2
        self.stats = stats

        # current status of the simulation
        self.sim_score1 = 0
        self.sim_score2 = 0
        self.game_to = 10

    """
    Returns true if the game is over/ either player has self.game_to goals
    """
    def is_over(self) -> bool:
        return self.sim_score1 >= self.game_to or self.sim_score2 >= self.game_to

    """
    Adds a goal to the given player's score
    """
    def add_goal(self,player:str) -> None:
        if not self.is_over():
            if player == self.player1:
                self.sim_score1 += 1
            elif player == self.player2:
                self.sim_score2 += 1
    
    """
    The probability that player1 scores on player2 on a given point
    """
    def get_p1_goal_prob(self) -> float:
        p1_goals = self.stats.get_goals_scored_on(self.player1,self.player2)
        p2_goals = self.stats.get_goals_scored_on(self.player2,self.player1)
        return (p1_goals+self.sim_score1+1)/(p1_goals+p2_goals+self.sim_score1+self.sim_score2+2)

    """
    Simulates a singular goal using self.get_p1_goal_prob()
    """
    def simulate_goal(self) -> None:
        if not self.is_over():
            rand = random.random()
            if rand < self.get_p1_goal_prob():
                self.sim_score1 += 1
            else:
                self.sim_score2 += 1

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
        return foosballgame.get_win_prob(self.get_p1_goal_prob(),self.sim_score1,self.sim_score2,self.game_to)

    """
    Returns the expected score for the given player given the current status of the simulation
    """
    def get_expected_score(self,player:str) -> float:
        if player == self.player1:
            goalprob = self.get_p1_goal_prob()
            pscore = self.sim_score1
            oppscore = self.sim_score2
        else:
            goalprob = 1-self.get_p1_goal_prob()
            pscore = self.sim_score2
            oppscore = self.sim_score1
        exp = 0
        for i in range(1,self.game_to+1):
            exp += i*foosballgame.get_prob_of_score(goalprob,i,pscore,oppscore,self.game_to)
        return exp

    """
    Returns the most probable score for te given player given the current status of the simulation
    """
    def get_most_probable_score(self, player:str) -> int:
        max_prob = 0
        score = 0
        for i in range(self.game_to):
            prob1 = foosballgame.get_prob_of_score(self.get_p1_goal_prob(),i,self.sim_score1,self.sim_score2,self.game_to)
            prob2 = foosballgame.get_prob_of_score(1-self.get_p1_goal_prob(),i,self.sim_score2,self.sim_score1,self.game_to)
            if prob1 > max_prob and prob1 > prob2:
                max_prob = prob1
                if player == self.player1:
                    score = i
                else:
                    score = self.game_to
            if prob2 > max_prob:
                max_prob = prob2
                if player == self.player1:
                    score = self.game_to
                else:
                    score = i
        return score