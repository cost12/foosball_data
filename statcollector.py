import pandas as pd
import random

import foosballgame
import gameinfo
import colley
import elo
import simulator
import event_date

"""
This class collects stats for a group of games
"""
class StatCollector:
    """
    Up next:
     - change internal representation for statcollector to dictionaries
        - need to learn how to get double dict to dataframe in correct way
     - 
    TO DO:
     - game watch/input
     - better/more options for filter
     - text to show selections/filter
     - games/probabilities
    """
    def __init__(self, games:foosballgame.FoosballGame) -> None:
        # games for which stats are collected
        self.games = []

        # stat categories that are collected
        self.stat_categories = ['players','matchups','games']

        # TODO: these may be useful/implemented later but not now
        #self.matchups = foosballgame.get_matchups(self.games)
        #self.filtered = games

        # dictionaries
        self.individual_dict = {}
        self.matchup_dict = {}

        # elo
        self.elo_tracker = elo.ELO_Calculator()

        # dataframes
        self.individual_stats = None
        self.matchup_stats = None
        self.game_stats = None

        # fill dataframes
        self.__init_dicts(games)
        self.__build_dfs()

    """
    Update/ build the dataframes used 
    """
    def __build_dfs(self) -> None:
        data_g = {} # this can't be calculated with the others because it depends on all time matchups
        for game in self.games:
            w_goals = self.matchup_dict[game.winner+game.loser]['GF']+1
            l_goals = self.matchup_dict[game.winner+game.loser]['GA']+1
            t_goals = w_goals + l_goals
            gp = self.matchup_dict[game.winner+game.loser]['W']+self.matchup_dict[game.winner+game.loser]['L']

            g_prob1 = 100*foosballgame.game_prob(w_goals/t_goals, game, or_less_likely_game=False, 
                                                 games_played=gp, given_total_games_played=False)
            
            g_prob2 = 100*foosballgame.game_prob(w_goals/t_goals, game, or_less_likely_game=True, 
                                                 games_played=gp, given_total_games_played=False)
            
            g_prob3 = 100*foosballgame.game_prob(w_goals/t_goals, game, or_less_likely_game=True, 
                                                 games_played=gp, given_total_games_played=True)
            
            g_prob4 = 100*foosballgame.game_prob(w_goals/t_goals, game, or_less_likely_game=False, 
                                                 games_played=gp, given_total_games_played=True)
            
            data_g[game.number] = {'Winner':game.winner,'Loser':game.loser,'Winner Score':game.winner_score,
                                   'Loser Score':game.loser_score,'Winner Color':game.winner_color,
                                   'Date':game.date,'Number':game.number,'G PROB':g_prob1,'LL PROB':g_prob2,
                                   'LL EXIST PROB':g_prob3,'EXIST PROB':g_prob4}

        self.game_stats = pd.DataFrame.from_dict(data_g,orient='index')

        self.individual_stats = pd.DataFrame.from_dict(self.individual_dict,orient='index')
        self.individual_stats = self.__calculate_final_columns(self.individual_stats)
        stats = ['Name','G','W','L','W PCT','STRK','GF','GA','G PCT','W PROB','WOE','LWS','LLS']
        self.individual_stats = self.individual_stats[stats]

        stats.insert(1,'Opponent')
        self.matchup_stats = pd.DataFrame.from_dict(self.matchup_dict,orient='index')
        self.matchup_stats = self.__calculate_final_columns(self.matchup_stats)
        self.matchup_stats = self.matchup_stats[stats]

        colley_w = colley.get_colley_rankings(self.games,by_wins=True)
        colley_g = colley.get_colley_rankings(self.games,by_wins=False)
        colley_w = pd.DataFrame.from_dict(colley_w,orient='index')
        colley_g = pd.DataFrame.from_dict(colley_g,orient='index')
        self.individual_stats = self.individual_stats.merge(colley_w)
        self.individual_stats = self.individual_stats.merge(colley_g)

        self.individual_stats = self.individual_stats.merge(self.elo_tracker.to_df())
        
    """
    Adds the last few columns onto the dataframes
    """
    def __calculate_final_columns(self,df:pd.DataFrame) -> pd.DataFrame:
        df['G'] = df['W']+df['L']
        df['W PCT'] = df['W']/df['G']
        df['G PCT'] = df['GF']/(df['GF']+df['GA'])
        df['W PROB'] = foosballgame.get_win_prob((df['GF']+1.0)/(df['GF']+df['GA']+2.0))
        df['WOE'] = df['W'] - df['W PROB']*df['G']
        df['STRK'] = df['Streak'].apply(lambda x : x.get_current_streak())
        df['LWS'] = df['Streak'].apply(lambda x : x.get_max_streak('W'))
        df['LLS'] = df['Streak'].apply(lambda x : x.get_max_streak('L'))
        return df

    """
    Initially add all data from the starting games into the individual and matchup dictionaries
    """
    def __init_dicts(self,games:list[foosballgame.FoosballGame]) -> None:
        for game in games:
            self.add_game(game)

    """
    Adds a list of games to the dataset
    """
    def add_games(self,games:list[foosballgame.FoosballGame]) -> None:
        for game in games:
            self.add_game(game)
        self.__build_dfs()
    
    """
    Add a game into the stat collector
    Updates the dictionaries and elo with the new game
    Optionally update the dataframe
    """
    def add_game(self, game:foosballgame.FoosballGame, update_df:bool=False) -> None:
        self.games.append(game)
        self.elo_tracker.add_game(game)

        # Commented out lines are for if TODO below works
        if game.winner not in self.individual_dict:
            self.individual_dict[game.winner] = {'Name':game.winner,'W':0,'L':0,'GF':0,'GA':0,'Streak':gameinfo.StreakKeeper()}
            #data2[game.winner] = {}
            #data2[game.winner+game.loser] = {'Player1':game.winner,'Player2':game.loser,'W':0,'L':0,'GF':0,'GA':0}
        if game.loser not in self.individual_dict:
            self.individual_dict[game.loser] = {'Name':game.loser,'W':0,'L':0,'GF':0,'GA':0,'Streak':gameinfo.StreakKeeper()}
            #data2[game.loser] = {}
            #data2[game.loser+game.winner] = {'Player1':game.loser,'Player2':game.winner,'W':0,'L':0,'GF':0,'GA':0}
        
        # TODO: find a way to make this work as a double dict
        if game.winner+game.loser not in self.matchup_dict:
            self.matchup_dict[game.winner+game.loser] = {'Name':game.winner,'Opponent':game.loser,'W':0,'L':0,'GF':0,'GA':0,'Streak':gameinfo.StreakKeeper()}
        if game.loser+game.winner not in self.matchup_dict:
            self.matchup_dict[game.loser+game.winner] = {'Name':game.loser,'Opponent':game.winner,'W':0,'L':0,'GF':0,'GA':0,'Streak':gameinfo.StreakKeeper()}

        self.individual_dict[game.winner]['W'] += 1
        self.individual_dict[game.winner]['GF'] += game.winner_score
        self.individual_dict[game.winner]['GA'] += game.loser_score
        self.individual_dict[game.winner]['Streak'].add_result('W')

        self.matchup_dict[game.winner+game.loser]['W'] += 1
        self.matchup_dict[game.winner+game.loser]['GF'] += game.winner_score
        self.matchup_dict[game.winner+game.loser]['GA'] += game.loser_score
        self.matchup_dict[game.winner+game.loser]['Streak'].add_result('W')

        self.individual_dict[game.loser]['L'] += 1
        self.individual_dict[game.loser]['GF'] += game.loser_score
        self.individual_dict[game.loser]['GA'] += game.winner_score
        self.individual_dict[game.loser]['Streak'].add_result('L')

        self.matchup_dict[game.loser+game.winner]['L'] += 1
        self.matchup_dict[game.loser+game.winner]['GF'] += game.loser_score
        self.matchup_dict[game.loser+game.winner]['GA'] += game.winner_score
        self.matchup_dict[game.loser+game.winner]['Streak'].add_result('L')

        if update_df:
            self.__build_dfs()

    """
    Returns a list of the stat categories
    """
    def list_stats(self) -> list[str]:
        return list(self.stat_categories)
    
    """ TODO: implement to not use df here, implement so df only updated when needed
    Returns a list of the players who have competed
    """
    def list_players(self) -> list[str]:
        return self.individual_stats['Name'].tolist()
    
    """
    Returns the number of goals player1 has scored on player2
    """
    def get_goals_scored_on(self, player1:str, player2:str) -> int:
        if (player1+player2) in self.matchup_dict: 
            return self.matchup_dict[player1+player2]['GF']
        else:
            return 0
        
    """
    Returns the number of wins player1 has against player2
    """
    def get_wins_against(self, player1:str, player2:str) -> int:
        if (player1+player2) in self.matchup_dict: 
            return self.matchup_dict[player1+player2]['W']
        else:
            return 0

    """
    Returns the dataframe for a given stat category
    """
    def get_stats(self, stat:str) -> pd.DataFrame:
        if stat == 'players':
            return self.individual_stats
        elif stat == 'matchups':
            return self.matchup_stats[self.matchup_stats['W'] > self.matchup_stats['L']]
        elif stat == 'games':
            return self.game_stats
        elif stat in self.stat_categories:
            print("Error: no stats for {}".format(stat))

    """
    Returns a simulator for p1 and p2
    """
    def get_simulator(self,p1:str,p2:str) -> simulator.Simulator:
        return simulator.Simulator(p1,p2,self)

    """
    Filters the games by selecting ones from the given timeframe and returns a new StatCollector
    """
    def filter_by_date(self,event_date:event_date.EventDate): # TODO: figure out how to type hint here
        games = []
        for game in self.games:
            if event_date.contains_date(game.date):
                games.append(game)
        return StatCollector(games)
    