#https://towardsdatascience.com/generate-sports-rankings-with-data-science-4dd1979571da

import numpy as np

import foosballgame

# if by_wins is false, ranking will be by score
# optionally pass in weights for games
def get_colley_rankings(games, by_wins = True, weighting = None, as_dict=False) -> dict[str,dict[str,str|float]]:
	players = list(foosballgame.get_player_range(games))
	c,b = __get_matrices(games,players,by_wins,weighting)
	by = 'W'
	if not by_wins:
		by = 'G'
	return __calculate_values(c,b,players,as_dict,by)

def get_colley_from_df(df,by='W'):
	players = list(df['Name'].unique())
	print(players[0])
	c,b = __matrices_from_df(df,by)
	return __calculate_values(c,b,players,False,by)
	
def __calculate_values(c,b,players,as_dict,by=None):
	c2 = np.array(c)
	b2 = np.array(b)

	diag = c2.diagonal() + 2
	np.fill_diagonal(c2, diag)

	for i in range(0,len(b2)):
		b2[i] = b2[i] / 2
		b2[i] += 1

	r = np.linalg.solve(c2, b2)

	if as_dict:
		rankings = {}
		for i in range(0,len(players)):
			rankings[players[i]] = r[i]
		return rankings
	else:
		rankings = {}
		for i in range(0,len(players)):
			rankings[players[i]] = {'Name':players[i], str(by)+' RANK':r[i]}
		return rankings

def __matrices_from_df(df, players, by='W'):
	num_players = len(players)
	c = np.zeros([num_players, num_players])
	b = np.zeros(num_players)
	
	for r in range(df.shape[0]):
		name1 = df.iloc[r]['Name']
		name2 = df.iloc[r]['Opponent']
		val = df.iloc[r][by]
		print(name1)
		index1 = players.index(name1)
		index2 = players.index(name2)
		c[index1][index1] += val
		c[index2][index2] += val
		c[index1][index2] -= val
		c[index2][index1] -= val
		b[index1] += val
		b[index2] -= val
	return c,b

def __get_matrices(games, players, by_wins = True, weighting = None):
	if weighting == None:
		weighting = np.ones(len(games))

	num_players = len(players)
	c = np.zeros([num_players, num_players])
	b = np.zeros(num_players)

	i = 0
	for game in games:
		update_matrices(game,c,b,players,weighting[i],by_wins)
		i += 1
	return c,b

# give a weight to each game depending on how long ago it was
# optionally take into account if players have played recently
def get_weights(data, weight_recent = True, initial_warmup = False, consider_warmup = False, absence_decay = 1, warmup_rate = 1):
	pass

def nice_print(rankings):
	to_print = list()
	for name in rankings.keys():
		to_print.append("%.4f" % rankings[name] + " " + name)
	to_print.sort(reverse = True)
	for line in to_print:
		print("\t" + line)


def update_matrices(game,c:np.ndarray,b:np.ndarray,players:list[str],weight:float,by_wins:bool):
	w_index = players.index(game.winner)
	l_index = players.index(game.loser)
	w_score = game.winner_score
	l_score = game.loser_score

	if by_wins:
		c[w_index][w_index] += weight # Updating diagonal element
		c[l_index][l_index] += weight # Updating diagonal element
		c[w_index][l_index] -= weight # Updating off - diagonal element
		c[l_index][w_index] -= weight # Updating off - diagonal element

		b[w_index] += weight
		b[l_index] -= weight
	else:
		c[w_index][w_index] += (w_score + l_score) * weight # Updating diagonal element
		c[l_index][l_index] += (w_score + l_score) * weight # Updating diagonal element
		c[w_index][l_index] -= (w_score + l_score) * weight # Updating off - diagonal element
		c[l_index][w_index] -= (w_score + l_score) * weight # Updating off - diagonal element

		b[w_index] += (w_score) * weight
		b[l_index] -= (w_score) * weight
		b[w_index] -= (l_score) * weight
		b[l_index] += (l_score) * weight

def get_rankings_list(games:list, xlist:list, sel_players:list[str], all_players:list[str], is_daily:bool, by_wins:bool,*, day_decay:float=1, game_decay:float=1) -> dict[str:float]:
	rankings = {}

	num_players = len(all_players)
	c = np.zeros([num_players, num_players])
	b = np.zeros(num_players)

	for player in sel_players:
		rankings[player] = [] #np.zeros(len(xlist))
	
	today = None
	i = 0
	g = 0
	while i < len(xlist):# g < len(games):
		while g < len(games) and i < len(xlist) and ((is_daily and games[g].date <= xlist[i]) or ((not is_daily) and games[g].number <= xlist[i])):
			if today is None:
				days = 0
			else:
				days = (games[g].date-today).days
			decay = game_decay*(day_decay**days)
			c *= decay
			b *= decay
			update_matrices(games[g],c,b,all_players,1,by_wins)
			today = games[g].date
			g += 1
		temp_ranks = __calculate_values(c,b,all_players,True)

		for player in sel_players:
			if player in temp_ranks.keys():
				rankings[player].append(temp_ranks[player])
			else:
				rankings[player].append(0)
		i += 1
	return rankings