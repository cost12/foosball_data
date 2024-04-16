import foosballgame

class SheetIdentifier:

    def __init__(self, name, id, sheet, csv = None) -> None:
        self.name = name          # readable name
        self.id = id              # id of shared sheet
        self.sheet_name = sheet   # name of sheet within the google sheets doc
        self.csv_name = csv       # name of the csv associated with the google sheets

        # name should be unique for all
        # csv_name should be unique for all


class Tracker(dict):
    """
    Custom dictionary class where default values are 0 and multiplication is defined for a float times a Tracker
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __missing__(self,key):
        return 0
    
    def __setitem__(self, key, value):
        if value==0:
            if key in self:  # returns zero anyway, so no need to store it
                del self[key]
        else:
            super().__setitem__(key, value)
    
    def __mul__(self, num):
        if num == 0:
            self.clear()
        for key in self:
            self[key] *= num
        return self

    def __rmul__(self, num):
        return self.__mul__(num)
    
    def times(self, num):
        self.__mul__(num)

def wins_step(game, totals):
    totals[game.winner] += 1

def games_step(game, totals):
    totals[game.winner] += 1
    totals[game.loser] += 1

def goals_step(game, totals):
    totals[game.winner] += game.winner_score
    totals[game.loser] += game.loser_score

def gf_avg_step(game, totals):
    if game.winner not in totals:
        totals[game.winner] = Tracker()
    if game.loser not in totals:
        totals[game.loser] = Tracker()
    totals[game.winner]['GOALS'] += game.winner_score
    totals[game.winner]['G'] += 1
    totals[game.loser]['GOALS'] += game.loser_score
    totals[game.loser]['G'] += 1

def ga_avg_step(game, totals):
    if game.winner not in totals:
        totals[game.winner] = Tracker()
    if game.loser not in totals:
        totals[game.loser] = Tracker()
    totals[game.winner]['GOALS'] += game.loser_score
    totals[game.winner]['G'] += 1
    totals[game.loser]['GOALS'] += game.winner_score
    totals[game.loser]['G'] += 1

def goals_avg_combine(player_total):
    if player_total == 0 or player_total['G'] == 0:
        return 0
    return player_total['GOALS']/player_total['G']

def win_pct_step(game, totals):
    if game.winner not in totals:
        totals[game.winner] = Tracker()
    if game.loser not in totals:
        totals[game.loser] = Tracker()
    totals[game.winner]['W'] += 1
    totals[game.winner]['G'] += 1
    totals[game.loser]['G'] += 1

def win_pct_combine(player_total):
    if player_total == 0 or player_total['G'] == 0:
        return 0
    return player_total['W']/player_total['G']

def win_prob_step(game, totals):
    if game.winner not in totals:
        totals[game.winner] = Tracker()
    if game.loser not in totals:
        totals[game.loser] = Tracker()
    totals[game.winner]['GF'] += game.winner_score
    totals[game.winner]['TG'] += game.loser_score + game.winner_score
    totals[game.loser]['GF'] += game.loser_score
    totals[game.loser]['TG'] += game.loser_score + game.winner_score

def win_prob_combine(player_total):
    if player_total == 0:
        return 0
    return foosballgame.get_win_prob((player_total['GF']+1)/(player_total['TG']+2))

def wins_over_exp_step(game, totals):
    if game.winner not in totals:
        totals[game.winner] = Tracker()
    if game.loser not in totals:
        totals[game.loser] = Tracker()
    totals[game.winner]['W'] += 1
    totals[game.winner]['G'] += 1
    totals[game.winner]['GF'] += game.winner_score
    totals[game.winner]['TG'] += game.loser_score + game.winner_score
    totals[game.loser]['GF'] += game.loser_score
    totals[game.loser]['TG'] += game.loser_score + game.winner_score
    totals[game.loser]['G'] += 1

def wins_over_exp_combine(player_total):
    if player_total == 0:
        return 0
    return player_total['W'] - player_total['G']*foosballgame.get_win_prob((player_total['GF']+1)/(player_total['TG']+2))

def streaks_step(game, totals):
    if totals[game.winner] > 0:
        totals[game.winner] += 1
    else:
        totals[game.winner] = 1

    if totals[game.loser] < 0:
        totals[game.loser] -= 1
    else:
        totals[game.loser] = -1

def get_player_lists(games, step_func, players, x_list, is_daily,*, combine=lambda x:x, day_decay:float=1, game_decay:float=1, last_n:int=None):
    totals = Tracker()
    player_lists = {}
    for player in players:
        player_lists[player] = [0] * len(x_list)
    i = 0
    g = 0
    today = None
    while i < len(x_list):# g < len(games):
        while g < len(games) and i < len(x_list) and ((is_daily and games[g].date <= x_list[i]) or ((not is_daily) and games[g].number <= x_list[i])):
            totals.times(game_decay)
            if today is None:
                days = 0
            else:
                days = (games[g].date-today).days
            totals.times(day_decay**days)
            today = games[g].date

            step_func(games[g],totals)
            #for player,num in update:
            #    totals[player] += num
            g += 1
        for player in players:
            player_lists[player][i] = combine(totals[player])
        i += 1
    return player_lists


if __name__=="__main__":
    test = Tracker()
    test[1] = 5
    test.times(0.99)
    test[1] += 2
    print(test[1])
    test.times(0.99)
    test[1] += 2
    print(test)
    print(test[1])