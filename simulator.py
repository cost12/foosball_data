import random

import statcollector as sc
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

    def __init__(self,p1:str,p2:str): 
        # the players being simulated
        self.player1 = p1
        self.player2 = p2

        # stat collector that includes all relevant games between player1 and player2
        self.stats = None
        self.attached = False

        # current status of the simulation
        self.sim_score1 = 0
        self.sim_score2 = 0
        self.game_to = 10

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
        if p1 is not None:
            self.player1 = p1
        if p2 is not None:
            self.player2 = p2
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
    Get the total goals scored for player1 against player2 in all games
    """
    def get_goals_for(self, player:str) -> int:
        if player == self.player1:
            return self.stats.get_goals_scored_on(self.player1,self.player2)
        elif player == self.player2:
            return self.stats.get_goals_scored_on(self.player2,self.player1)
        else:
            return 0
    
    """
    Get the total wins for player1 against player2 in all games
    """
    def get_wins_for(self, player:str) -> int:
        if player == self.player1:
            return self.stats.get_wins_against(self.player1,self.player2)
        elif player == self.player2:
            return self.stats.get_wins_against(self.player2,self.player1)
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
    Return the probability that the given player gets the given score
    """
    def get_prob_of_score(self, player:str, score:int) -> float:
        if player == self.player1:
            return foosballgame.get_prob_of_score(self.get_p1_goal_prob(),score,self.sim_score1,self.sim_score2,self.game_to)
        elif player == self.player2:
            return foosballgame.get_prob_of_score(1-self.get_p1_goal_prob(),score,self.sim_score2,self.sim_score1,self.game_to)
        else:
            if score == 0:
                return 1
            else:
                return 0
            
    """
    Get the number of times a player scored score goals against the other player
    """
    def get_times_scored_n(self, player:str, score:int) -> int:
        if player == self.player1:
            return self.stats.get_times_scored_n(self.player1, self.player2, score)
        elif player == self.player2:
            return self.stats.get_times_scored_n(self.player2, self.player1, score)
        else:
            return 0

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
    
class SkillSimulator(Simulator):

    def __init__(self,p1:str,p2:str):
        super().__init__(p1,p2)

    def get_p1_goal_prob(self) -> float:
        p1_skill = self.stats.skill_tracker.get_rating(self.player1)
        p2_skill = self.stats.skill_tracker.get_rating(self.player2)
        return p1_skill/(p1_skill+p2_skill)

class ProbabilitySimulator(Simulator):

    def __init__(self,p1:str,p2:str):
        super().__init__(p1,p2)

    def get_p1_goal_prob(self) -> float:
        p1_goals = self.stats.get_goals_scored_on(self.player1,self.player2)
        p2_goals = self.stats.get_goals_scored_on(self.player2,self.player1)
        return (p1_goals+self.sim_score1+1)/(p1_goals+p2_goals+self.sim_score1+self.sim_score2+2)
    
def get_simulator(p1:str,p2:str,type:str):
    if type.lower() == 'skill':
        return SkillSimulator(p1,p2)
    if type.lower() in ['prob', 'probability']:
        return ProbabilitySimulator(p1,p2)
    else:
        print(f"Unknown simulator type {type}")
