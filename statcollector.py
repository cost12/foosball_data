import pandas as pd
import random

import foosballgame
import gameinfo
import colley
import event_date

class Simulator:

    def __init__(self,p1,p2,p1g=0,p2g=0):
        self.player1 = p1
        self.player2 = p2
        self.p1_goals = p1g
        self.p2_goals = p2g

        self.sim_score1 = 0
        self.sim_score2 = 0
        self.game_to = 10

    def is_over(self):
        return self.sim_score1 >= self.game_to or self.sim_score2 >= self.game_to

    def add_goal(self,player):
        if not self.is_over():
            if player == self.player1:
                self.sim_score1 += 1
            elif player == self.player2:
                self.sim_score2 += 1
    
    def get_p1_goal_prob(self):
        return (self.p1_goals+self.sim_score1+1)/(self.p1_goals+self.p2_goals+self.sim_score1+self.sim_score2+2)

    def get_p1_win_odds(self):
        return foosballgame.get_win_prob(self.get_p1_goal_prob(),self.sim_score1,self.sim_score2,self.game_to)

    def get_expected_score(self,player):
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

    def get_most_probable_score(self, player):
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

    def simulate_game(self):
        while not self.is_over():
            self.simulate_goal()

    def simulate_goal(self):
        if not self.is_over():
            rand = random.random()
            if rand < self.get_p1_goal_prob():
                self.sim_score1 += 1
            else:
                self.sim_score2 += 1

class StatCollector:
    """
    Up next:
     - 
     - 
    TO DO:
     - simulation
     - game watch/input
     - better/more options for filter
     - text to show selections/filter
    """
    def __init__(self, games):
        self.games = games
        #self.matchups = foosballgame.get_matchups(self.games)
        #self.filtered = games
        self.stats = ['players','matchups']
        self.individual_stats = None
        self.matchup_stats = None
        self.__calculate_stats()

    def __calculate_stats(self):
        data_i,data_m = self.__get_data(self.games)

        self.individual_stats = pd.DataFrame.from_dict(data_i,orient='index')
        self.individual_stats = self.__calculate_final_columns(self.individual_stats)
        stats = ['Name','G','W','L','W PCT','STRK','GF','GA','G PCT','W PROB','WOE','LWS','LLS']
        self.individual_stats = self.individual_stats[stats]

        stats.insert(1,'Opponent')
        self.matchup_stats = pd.DataFrame.from_dict(data_m,orient='index')
        self.matchup_stats = self.__calculate_final_columns(self.matchup_stats)
        self.matchup_stats = self.matchup_stats[stats]

        colley_w = colley.get_colley_rankings(self.games,by_wins=True)
        colley_g = colley.get_colley_rankings(self.games,by_wins=False)
        colley_w = pd.DataFrame.from_dict(colley_w,orient='index')
        colley_g = pd.DataFrame.from_dict(colley_g,orient='index')
        self.individual_stats = self.individual_stats.merge(colley_w)
        self.individual_stats = self.individual_stats.merge(colley_g)

    def __calculate_final_columns(self,df):
        df['G'] = df['W']+df['L']
        df['W PCT'] = df['W']/df['G']
        df['G PCT'] = df['GF']/(df['GF']+df['GA'])
        df['W PROB'] = foosballgame.get_win_prob((df['GF']+1.0)/(df['GF']+df['GA']+2.0))
        df['WOE'] = df['W'] - df['W PROB']*df['G']
        df['STRK'] = df['Streak'].apply(lambda x : x.get_current_streak())
        df['LWS'] = df['Streak'].apply(lambda x : x.get_max_streak('W'))
        df['LLS'] = df['Streak'].apply(lambda x : x.get_max_streak('L'))
        return df

    def __get_data(self,games):
        data = {}
        data2 = {}
        for game in games:
            if game.winner not in data:
                data[game.winner] = {'Name':game.winner,'W':0,'L':0,'GF':0,'GA':0,'Streak':gameinfo.StreakKeeper()}
                #data2[game.winner] = {}
                #data2[game.winner+game.loser] = {'Player1':game.winner,'Player2':game.loser,'W':0,'L':0,'GF':0,'GA':0}
            if game.loser not in data:
                data[game.loser] = {'Name':game.loser,'W':0,'L':0,'GF':0,'GA':0,'Streak':gameinfo.StreakKeeper()}
                #data2[game.loser] = {}
                #data2[game.loser+game.winner] = {'Player1':game.loser,'Player2':game.winner,'W':0,'L':0,'GF':0,'GA':0}
            
            if game.winner+game.loser not in data2:
                data2[game.winner+game.loser] = {'Name':game.winner,'Opponent':game.loser,'W':0,'L':0,'GF':0,'GA':0,'Streak':gameinfo.StreakKeeper()}
            if game.loser+game.winner not in data2:
                data2[game.loser+game.winner] = {'Name':game.loser,'Opponent':game.winner,'W':0,'L':0,'GF':0,'GA':0,'Streak':gameinfo.StreakKeeper()}

            data[game.winner]['W'] += 1
            data[game.winner]['GF'] += game.winner_score
            data[game.winner]['GA'] += game.loser_score
            data[game.winner]['Streak'].add_result('W')

            data2[game.winner+game.loser]['W'] += 1
            data2[game.winner+game.loser]['GF'] += game.winner_score
            data2[game.winner+game.loser]['GA'] += game.loser_score
            data2[game.winner+game.loser]['Streak'].add_result('W')

            data[game.loser]['L'] += 1
            data[game.loser]['GF'] += game.loser_score
            data[game.loser]['GA'] += game.winner_score
            data[game.loser]['Streak'].add_result('L')

            data2[game.loser+game.winner]['L'] += 1
            data2[game.loser+game.winner]['GF'] += game.loser_score
            data2[game.loser+game.winner]['GA'] += game.winner_score
            data2[game.loser+game.winner]['Streak'].add_result('L')

        return data,data2

    def list_stats(self):
        return list(self.stats)
    
    def list_players(self):
        return self.individual_stats['Name'].tolist()

    def get_stats(self, stat):
        if stat == 'players':
            return self.individual_stats
        elif stat == 'matchups':
            return self.matchup_stats[self.matchup_stats['W'] > self.matchup_stats['L']]
        elif stat in self.stats:
            print("Error: no stats for {}".format(stat))

    def get_simulator(self,p1,p2) -> Simulator:
        row = self.matchup_stats.loc[(self.matchup_stats['Name']==p1)&(self.matchup_stats['Opponent']==p2)]
        if len(row) > 0:
            p1g = row['GF'][0]
            p2g = row['GA'][0]
        else:
            p1g = 0
            p2g = 0
        return Simulator(p1,p2,p1g,p2g)

    def filter_by_date(self,event_date):
        games = []
        for game in self.games:
            if event_date.contains_date(game.date):
                games.append(game)
        return StatCollector(games)