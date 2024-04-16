import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

"""
Creates and returns a formatted graph
"""
def create_foosball_graph(name:str, xlabel:str, ylabel:str, players:list[str], xlist:list, rankings:dict[str,list], remove_zeros:bool=True, ignore_players:list[str]=[], scatter:bool=False):
	fig = plt.figure()
	plt.title(name)
	plt.xlabel(xlabel)
	plt.ylabel(ylabel)
	for player in players:
		if player in ignore_players:
			continue
		x = xlist
		y = rankings[player]
		new_x = []
		new_y = []
		for i in range(0,len(x)):
			if y[i] != 0 or not remove_zeros:
				new_x.append(x[i])
				new_y.append(y[i])
		if len(new_x) > 0:
			if scatter: 
				plt.scatter(new_x, new_y, label = player)
			else:
				plt.plot(new_x, new_y, label = player)
			plt.annotate(xy=(new_x[-1], new_y[-1]), xytext=(20,0), textcoords='offset points', text=player, va='center')
	plt.gca().tick_params(axis='x', labelrotation = 90)
	fig.tight_layout()
	return fig
	#fig.savefig("graphs/" + filename)

"""
Creates a list for each player in players
function: computes a statistic from a list of games, returns a map from players to their value

"""
def get_list_over_range(games, xlist, players, function, is_daily, modifier=lambda x : x):
	player_lists = {}
	# create a list for each player over the x values
	for player in players:
		player_lists[player] = []
	
	for x in xlist:
		temp = []
		for game in games:
			if (is_daily and game.date <= x) or ((not is_daily) and game.number <= x):
				temp.append(game)
		temp_values = function(temp) # function must be a lambda function with values filled out other than games to be passed in
		                             # must return a map from player to value
		for player in players:
			if player in temp_values.keys():
				player_lists[player].append(modifier(temp_values[player]))
			else:
				player_lists[player].append(0)
	return player_lists