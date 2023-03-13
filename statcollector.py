import pandas as pd

import foosballgame

class StatCollector:
    """
    Things to track:
        - wins,losses,gf,ga
        - colley rankings: w,l
        - streaks: w,l,consecutive
        - matchups
        - count
        - by date
        - filter
        - normalized records
        - expected w,l,pct
        - avg goals w,l
        - win prob
        - most/least probable
        - sim?
        - by semester
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
        self.individual_stats = self.individual_stats[['Name','W','L','W PCT','GF','GA','G PCT']]

        self.matchup_stats = pd.DataFrame.from_dict(data_m,orient='index')
        self.matchup_stats = self.__calculate_final_columns(self.matchup_stats)
        self.matchup_stats = self.matchup_stats[['Player1','Player2','W','L','W PCT','GF','GA','G PCT']]

    def __calculate_final_columns(self,df):
        df['W PCT'] = df['W']/(df['W']+df['L'])
        df['G PCT'] = df['GF']/(df['GF']+df['GA'])
        return df

    def __get_data(self,games):
        data = {}
        data2 = {}
        for game in games:
            if game.winner not in data:
                data[game.winner] = {'Name':game.winner,'W':0,'L':0,'GF':0,'GA':0}
                #data2[game.winner] = {}
                #data2[game.winner+game.loser] = {'Player1':game.winner,'Player2':game.loser,'W':0,'L':0,'GF':0,'GA':0}
            if game.loser not in data:
                data[game.loser] = {'Name':game.loser,'W':0,'L':0,'GF':0,'GA':0}
                #data2[game.loser] = {}
                #data2[game.loser+game.winner] = {'Player1':game.loser,'Player2':game.winner,'W':0,'L':0,'GF':0,'GA':0}
            
            if game.winner+game.loser not in data2:
                data2[game.winner+game.loser] = {'Player1':game.winner,'Player2':game.loser,'W':0,'L':0,'GF':0,'GA':0}
            if game.loser+game.winner not in data2:
                data2[game.loser+game.winner] = {'Player1':game.loser,'Player2':game.winner,'W':0,'L':0,'GF':0,'GA':0}

            data[game.winner]['W'] += 1
            data[game.winner]['GF'] += game.winner_score
            data[game.winner]['GA'] += game.loser_score

            data2[game.winner+game.loser]['W'] += 1
            data2[game.winner+game.loser]['GF'] += game.winner_score
            data2[game.winner+game.loser]['GA'] += game.loser_score

            data[game.loser]['L'] += 1
            data[game.loser]['GF'] += game.loser_score
            data[game.loser]['GA'] += game.winner_score

            data2[game.loser+game.winner]['L'] += 1
            data2[game.loser+game.winner]['GF'] += game.loser_score
            data2[game.loser+game.winner]['GA'] += game.winner_score

        return data,data2

    def list_stats(self):
        return list(self.stats)

    def get_stats(self, stat):
        if stat == 'players':
            return self.individual_stats
        elif stat == 'matchups':
            return self.matchup_stats[self.matchup_stats['W'] > self.matchup_stats['L']]
        elif stat in self.stats:
            print("Error: no stats for {}".format(stat))

    def filter_by(self, filter):
        pass

    def reset_filter(self):
        self.filtered = self.games