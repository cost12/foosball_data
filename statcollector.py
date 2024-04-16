import pandas as pd
import random
import datetime

import foosballgame
import gameinfo
import colley
import elo
import myranks
import event_date
import gamefilter

""" TODO: handle 0 games
This class collects stats for a group of games
"""
class StatCollector:
    """
    Up next:
     - change internal representation for statcollector to dictionaries
        - need to learn how to get double dict to dataframe in correct way
     - 
    TODO:
     - game watch/input
     - better/more options for filter
     - text to show selections/filter
     - games/probabilities
    """
    def __init__(self, games:foosballgame.FoosballGame) -> None:
        # keep track of whether the data has been changed and needs to be recalculated
        self.refiltered = True
        self.games_added = True

        # games for which stats are collected
        self.games = list[foosballgame.FoosballGame](games)

        # stat categories that are collected
        stats = ['Name','G','W','L','W PCT','STRK','GF','GA','G PCT','W PROB','WOE','LWS','LLS']
        ratings = ['W RANK', 'G RANK', 'ELO', 'GOAL ELO', 'Skill']
        games_stats = ['Winner', 'Loser', 'Winner Score', 'Loser Score', 'Winner Color', 'Date', 'Number', 'G PROB', 'LL PROB', 'LL EXIST PROB', 'EXIST PROB']
        self.stat_categories = dict[str,list[str]]( \
            {'standings': ['Name', 'G', 'W', 'L', 'W PCT', 'STRK', 'GF', 'GA', 'G PCT', 'LWS', 'LLS'], \
             'ratings':   ['Name', 'G', 'W', 'L', 'W PROB', 'WOE', 'Skill', 'W RANK', 'G RANK', 'ELO', 'GOAL ELO'], \
             'schedule':  ['Name', 'G', 'W', 'L', 'NW', 'NL', 'NW PCT', 'NSOS', 'NSOV', 'NSINDEX', 'SOS', 'SOV', 'SINDEX'], \
             'matchups':  ['Name', 'Opponent', 'G', 'W', 'L', 'W PCT', 'STRK', 'GF', 'GA', 'G PCT', 'LWS', 'LLS', 'W PROB', 'WOE'], \
             #'m ratings': ['Name', 'Opponent', 'G', 'W', 'L', 'W PROB', 'WOE'], \
             'games':     ['Winner', 'Loser', 'Winner Score', 'Loser Score', 'Winner Color', 'Date', 'Number', 'G PROB', 'LL PROB', 'LL EXIST PROB', 'EXIST PROB']} \
        )
        self.stats_from_players = set[str]({'standings', 'ratings', 'schedule', 'streaks'})
        self.stats_from_matchups = set[str]({'matchups', 'm ratings', 'm streaks'})
        self.stats_from_games = set[str]({'games'})

        # TODO: these may be useful/implemented later but not now
        #self.matchups = foosballgame.get_matchups(self.games)
        self.filtered = list[foosballgame.FoosballGame](games)

        # dictionaries, initiated in init_dicts
        #self.individual_dict = {}
        #self.matchup_dict = {}

        # ratings
        self.elo_tracker = elo.ELO_Calculator()
        self.skill_tracker = myranks.SkillRating('Skill')

        # dataframes
        self.individual_stats = None
        self.matchup_stats = None
        self.game_stats = None

        # fill dataframes
        self.__init_dicts(games)
        self.__build_dfs()

    """
    Recalculate all values, called when the filter changes
    """
    def __recalculate(self) -> None:
        self.__init_dicts(self.filtered)
        self.__build_dfs()

        

    """
    Call at the start of any function that uses internal dicts
    """
    def __uses_dicts(self) -> None:
        if self.refiltered:
            self.__recalculate()

    """
    Call at the start of any function that uses internal dfs
    """
    def __uses_dfs(self) -> None:
        if self.refiltered:
            self.__recalculate()
        elif self.games_added:
            self.__build_dfs()

    """
    Update/ build the dataframes used 
    """
    def __build_dfs(self) -> None:
        if len(self.filtered) == 0:
            return
        data_g = {} # this can't be calculated with the others because it depends on all time matchups
        for game in self.filtered:
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

        colley_w = colley.get_colley_rankings(self.filtered,by_wins=True)
        colley_g = colley.get_colley_rankings(self.filtered,by_wins=False)
        colley_w = pd.DataFrame.from_dict(colley_w,orient='index')
        colley_g = pd.DataFrame.from_dict(colley_g,orient='index')
        self.individual_stats = self.individual_stats.merge(colley_w,how='left')
        self.individual_stats = self.individual_stats.merge(colley_g,how='left')

        self.individual_stats = self.individual_stats.merge(self.elo_tracker.to_df(),how='left')
        self.individual_stats = self.individual_stats.merge(self.skill_tracker.to_df(),how='left')
        self.individual_stats = self.individual_stats.fillna(0)
        self.individual_stats = self.individual_stats.astype({'ELO':int,'GOAL ELO':int})
        
        self.individual_stats['NW'] = self.normed(wins=True)
        self.individual_stats['NL'] = self.normed(wins=False)
        self.individual_stats['NW PCT'] = self.individual_stats['NW']/(self.individual_stats['NL']+self.individual_stats['NW'])
        self.individual_stats['SOS'] = self.strength(victory=False)
        self.individual_stats['SOV'] = self.strength(victory=True)
        self.individual_stats['SINDEX'] = self.individual_stats['SOV']/self.individual_stats['SOS']
        self.individual_stats['NSOS'] = self.strength(victory=False,normalized=True)
        self.individual_stats['NSOV'] = self.strength(victory=True,normalized=True)
        self.individual_stats['NSINDEX'] = self.individual_stats['NSOV']/self.individual_stats['NSOS']

        self.games_added = False

    def strength(self, victory:bool, normalized:bool=False):
        """
        Calculates strength of schedule and strength of victory and returns an array
        Can also calculate normalized sos and sov
        """
        soss = []
        if victory:
            consider = 'W'
        else:
            consider = 'G'
        
        for player in self.individual_stats['Name']:
            wins = 0
            losses = 0
            for opponent in self.matchup_stats[self.matchup_stats['Name']==player]['Opponent']:
                g = self.matchup_stats[(self.matchup_stats['Name']==player) & (self.matchup_stats['Opponent']==opponent)][consider][0]
                if normalized:
                    pct = self.individual_stats[self.individual_stats['Name'] == opponent]['W PCT']
                    pct = list(pct)[0]
                    wins += pct*g
                    losses += (1-pct)*g
                else:
                    w = self.individual_stats[self.individual_stats['Name'] == opponent]['W']
                    w = list(w)[0]
                    wins += w*g
                    l = self.individual_stats[self.individual_stats['Name'] == opponent]["L"]
                    l = list(l)[0]
                    losses += l*g
            if wins > 0:
                soss.append(wins/(wins+losses))
            else:
                soss.append(0)
        return soss
    
    def normed(self, wins:bool):
        """
        Caluculates normalized wins or losses and returns in an array
        """
        totals = []

        for player in self.individual_stats['Name']:
            total = 0
            for opponent in self.matchup_stats[self.matchup_stats['Name']==player]['Opponent']:
                pct = self.matchup_stats[(self.matchup_stats['Name']==player) & (self.matchup_stats['Opponent']==opponent)]['W PCT'][0]
                if wins:
                    total += pct
                else:
                    total += 1-pct
            totals.append(total)
        return totals
        
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
        self.individual_dict = {}
        self.matchup_dict = {}
        self.elo_tracker = elo.ELO_Calculator()
        self.skill_tracker = myranks.SkillRating('Skill')
        for game in games:
            self.add_game(game, new_game=False)
        self.refiltered = False

    """
    Adds a list of games to the dataset
    """
    def add_games(self,games:list[foosballgame.FoosballGame]) -> None:
        for game in games:
            self.add_game(game)
            
    """
    Add a game into the stat collector
    Updates the dictionaries and elo with the new game
    Optionally update the dataframe
    """
    def add_game(self, game:foosballgame.FoosballGame, filter_in:bool=True, new_game = True) -> None:
        if new_game:
            self.games.append(game)
            if filter_in:
                self.filtered.append(game)
        self.elo_tracker.add_game(game)
        self.skill_tracker.add_game(game)

        if 'B' not in self.individual_dict:
            self.individual_dict['B'] = {'Name':'B','W':0,'L':0,'GF':0,'GA':0,'Streak':gameinfo.StreakKeeper()}
            self.individual_dict['W'] = {'Name':'W','W':0,'L':0,'GF':0,'GA':0,'Streak':gameinfo.StreakKeeper()}
            self.matchup_dict['BW'] = {'Name':'B','Opponent':'W','W':0,'L':0,'GF':0,'GA':0,'Streak':gameinfo.StreakKeeper()}
            self.matchup_dict['WB'] = {'Name':'W','Opponent':'B','W':0,'L':0,'GF':0,'GA':0,'Streak':gameinfo.StreakKeeper()}
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

        for w,l in [(game.winner, game.loser),(game.winner_color,game.loser_color())]:
            self.individual_dict[w]['W'] += 1
            self.individual_dict[w]['GF'] += game.winner_score
            self.individual_dict[w]['GA'] += game.loser_score
            self.individual_dict[w]['Streak'].add_result('W')

            self.individual_dict[l]['L'] += 1
            self.individual_dict[l]['GF'] += game.loser_score
            self.individual_dict[l]['GA'] += game.winner_score
            self.individual_dict[l]['Streak'].add_result('L')

            self.matchup_dict[w+l]['W'] += 1
            self.matchup_dict[w+l]['GF'] += game.winner_score
            self.matchup_dict[w+l]['GA'] += game.loser_score
            self.matchup_dict[w+l]['Streak'].add_result('W')

            self.matchup_dict[l+w]['L'] += 1
            self.matchup_dict[l+w]['GF'] += game.loser_score
            self.matchup_dict[l+w]['GA'] += game.winner_score
            self.matchup_dict[l+w]['Streak'].add_result('L')
        
        self.games_added = True

    """
    Returns a list of the stat categories
    """
    def list_stats(self) -> list[str]:
        return list(self.stat_categories)
    
    """
    Returns a list of the players who have competed
    """
    def list_players(self, selected_only=False) -> list[str]:
        if selected_only:
            game_space = self.filtered
        else:
            game_space = self.games
        players = set()
        players.add('W')
        players.add('B')
        for game in game_space:
            players.add(game.winner)
            players.add(game.loser)
        return list(players)

    def list_numbers(self, selected_only=False) -> list[int]:
        if selected_only:
            return [x.number for x in self.filtered]
        else:
            return [x.number for x in self.games]

    def list_dates(self, selected_only=False) -> list[datetime.date]:
        if selected_only:
            game_space = self.filtered
        else:
            game_space = self.games
        dates = []
        for game in game_space:
            if len(dates) == 0 or not (dates[-1] == game.date):
                dates.append(game.date)
        return dates

    """
    Returns the number of goals player1 has scored on player2
    """
    def get_goals_scored_on(self, player1:str, player2:str) -> int:
        self.__uses_dicts()
        if (player1+player2) in self.matchup_dict: 
            return self.matchup_dict[player1+player2]['GF']
        else:
            return 0
        
    """
    Returns the number of wins player1 has against player2
    """
    def get_wins_against(self, player1:str, player2:str) -> int:
        self.__uses_dicts()
        if (player1+player2) in self.matchup_dict: 
            return self.matchup_dict[player1+player2]['W']
        else:
            return 0
        
    """
    Returns the number of times player1 scored num goals against player2
    ANY can be passed for either player
    """
    def get_times_scored_n(self, player1:str, player2:str, num:int) -> int:
        count = 0
        for game in self.filtered:
            if (game.winner == player1 or player1 == 'ANY') and (game.loser == player2 or player2 == 'ANY'):
                if game.winner_score == num:
                    count += 1
            elif (game.loser == player1 or player1 == 'ANY') and (game.winner == player2 or player2 == 'ANY'):
                if game.loser_score == num:
                    count += 1
        return count

    """
    Returns the dataframe for a given stat category
    """
    def get_stats(self, stat:str) -> pd.DataFrame:
        self.__uses_dfs()
        if stat in self.stats_from_players:
            return self.individual_stats[self.stat_categories[stat]]
        elif stat in self.stats_from_matchups:
            # lots of tie breakers
            return self.matchup_stats[self.stat_categories[stat]].loc[(self.matchup_stats['W'] >  self.matchup_stats['L']) | 
                                         ((self.matchup_stats['W'] == self.matchup_stats['L']) & (self.matchup_stats['GF'] > self.matchup_stats['GA'])) | 
                                         ((self.matchup_stats['W'] == self.matchup_stats['L']) & (self.matchup_stats['GF'] == self.matchup_stats['GA']) & (self.matchup_stats['STRK'] < gameinfo.Streak(1,'W')))]
        elif stat in self.stats_from_games:
            return self.game_stats[self.stat_categories[stat]]
        elif stat in self.stat_categories:
            print("Error: no stats for {}".format(stat))

    def get_stat(self, stat:str, df:str) -> pd.DataFrame:
        self.__uses_dfs()
        if df == 'individual':
            return self.individual_stats[['Name', stat]]
        elif df == 'matchup':
            return self.matchup_stats[['Name', 'Opponent', stat]]
        elif df == 'games':
            return self.game_stats[['Number', stat]]
        
    def get_elo(self) -> elo.ELO_Calculator:
        self.__uses_dicts()
        return self.elo_tracker

    """
    Filters the games by selecting ones from the given timeframe and returns a new StatCollector, or updates the current one
    """
    def filter_by_date(self,event_date:event_date.EventDate,make_new:bool=False):
        filtered = []
        for game in self.games:
            if event_date.contains_date(game.date):
                filtered.append(game)

        if make_new:
            return StatCollector(filtered)
        else:
            if not self.filtered == filtered:
                self.filtered = filtered     
                self.refiltered = True

    """
    Applies a filter to the games
    Returns a new StatCollector or updates the current
    """
    def apply_filter(self, filter:gamefilter.GameFilter,make_new:bool=False) -> None:
        filtered = []
        for game in self.games:
            if filter.predicate(game):
                filtered.append(game)
        if make_new:
            return StatCollector(filtered)
        else:
            if not self.filtered == filtered:
                self.filtered = filtered     
                self.refiltered = True

    def set_games(self, games:list[foosballgame.FoosballGame]) -> None:
        self.games = games
        self.filtered = games
        self.__recalculate()

    """
    Count how many games would be selected by a given filter
    """
    def count_filtered(self, filter:gamefilter.GameFilter) -> int:
        count = 0
        for game in self.games:
            if filter.predicate(game):
                count += 1
        return count

    """
    Resets the filter to include all games
    """
    def reset_filter(self) -> None:
        self.filtered = list(self.games)
        self.refiltered = True

    # TODO: consolidate magic numbers
    def min_score_possible(self) -> int:
        return 0
    
    def max_score_possible(self) -> int:
        return 10
    
    def min_score_loss(self) -> int:
        min_ach = self.filtered[0].loser_score
        for game in self.filtered:
            if game.loser_score < min_ach:
                min_ach = game.loser_score
        return min_ach
    
    def max_score_loss(self) -> int:
        max_ach = self.filtered[0].loser_score
        for game in self.filtered:
            if game.loser_score > max_ach:
                max_ach = game.loser_score
        return max_ach
    
    def min_num(self) -> int:
        return self.games[0].number
    
    def max_num(self) -> int:
        return self.games[-1].number
    
    def min_num_selected(self) -> int:
        return self.filtered[0].number
    
    def max_num_selected(self) -> int:
        return self.filtered[-1].number
