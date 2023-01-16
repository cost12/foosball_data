import numpy as np

import foosballgame

# if by_wins is false, ranking will be by score
# optionally pass in weights for games
def get_colley_rankings(games, by_wins = True, weighting = None):
	if weighting == None:
		weighting = np.ones(len(games))

	players = list(foosballgame.get_player_range(games))

	num_players = len(players)
	c = np.zeros([num_players, num_players])
	b = np.zeros(num_players)

	i = 0
	for game in games:
		w_index = players.index(game.winner)
		l_index = players.index(game.loser)
		w_score = game.winner_score
		l_score = game.loser_score

		if by_wins:
			c[w_index][w_index] += weighting[i] # Updating diagonal element
			c[l_index][l_index] += weighting[i] # Updating diagonal element
			c[w_index][l_index] -= weighting[i] # Updating off - diagonal element
			c[l_index][w_index] -= weighting[i] # Updating off - diagonal element

			b[w_index] += weighting[i]
			b[l_index] -= weighting[i]
		else:
			c[w_index][w_index] += (w_score + l_score) * weighting[i] # Updating diagonal element
			c[l_index][l_index] += (w_score + l_score) * weighting[i] # Updating diagonal element
			c[w_index][l_index] -= (w_score + l_score) * weighting[i] # Updating off - diagonal element
			c[l_index][w_index] -= (w_score + l_score) * weighting[i] # Updating off - diagonal element

			b[w_index] += (w_score) * weighting[i]
			b[l_index] -= (w_score) * weighting[i]
			b[w_index] -= (l_score) * weighting[i]
			b[l_index] += (l_score) * weighting[i]
		i += 1

	diag = c.diagonal() + 2
	np.fill_diagonal(c, diag)

	for i in range(0,len(b)):
	    b[i] = b[i] / 2
	    b[i] += 1

	r = np.linalg.solve(c, b)

	rankings = {}
	for i in range(0,len(players)):
		rankings[players[i]] = r[i]
	return rankings

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


def get_rankings_list(games, xlist, players, is_daily, by_wins):
	rankings = {}

	for player in players:
		rankings[player] = [] #np.zeros(len(xlist))
	
	for x in xlist:
		temp = []
		for game in games:
			if (is_daily and game.date <= x) or ((not is_daily) and game.number <= x):
				temp.append(game)
		temp_ranks = get_colley_rankings(temp, by_wins = by_wins)
		for player in players:
			if player in temp_ranks.keys():
				rankings[player].append(temp_ranks[player])
			else:
				rankings[player].append(0)
	return rankings