import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import h5py

import old.graph as graph
import colley
import foosballgame
import graphsyousee
import userinput

def list_games(games):
	if len(games) == 0:
		return {}
	else:
		return {games[-1].winner:games[-1].winner_score, games[-1].loser:games[-1].loser_score}

def list_nums(games):
	nums = []
	for game in games:
		nums.append(game.number)
	return nums

file = "data/FoosballDataCollection.h5"

with h5py.File(file, "r") as games:
	# graph stuff
	win_graph = graph.Graph()
	goal_graph = graph.Graph()
	game_count = {}

	# FoosballGame stuff
	all_games = []

	i = 0
	while (len(games["Games"]["Location1"]['Winner Name'][i]) > 0):
		game = games["Games"]["Location1"][i]
		winner = str(game['Winner Name'])[2:-1]
		loser = str(game['Loser Name'])[2:-1]

		# graph stuff
		if winner in game_count:
			game_count[winner] += 1
		else:
			game_count[winner] = 1

		if loser in game_count:
			game_count[loser] += 1
		else:
			game_count[loser] = 1

		win_graph.add_edge(loser, winner, 1)
		goal_graph.add_edge(loser, winner, 10)
		goal_graph.add_edge(winner, loser, int(game['Loser Score']))

		# FoosballGame stuff
		all_games.append(foosballgame.FoosballGame(winner, loser, 10, int(game['Loser Score']), str(game['Winner Color'])[2:-1], datetime.strptime(str(game['Date'])[2:-1], '%Y-%m-%d'),int(game['Number'])))

		i += 1

	userinput.interaction(all_games)
	
	print_rankings = False
	if print_rankings:
		print("By wins:")
		colley.nice_print(colley.get_colley_rankings(all_games))
		print("By goals:")
		colley.nice_print(colley.get_colley_rankings(all_games, by_wins = False))
	
	update_graphs = False
	if update_graphs:

		dates = foosballgame.get_date_range(all_games)
		nums =  foosballgame.get_num_range(all_games)
		players = foosballgame.get_player_range(all_games)

		daily_win_rankings =  colley.get_rankings_list(all_games, dates, players, is_daily = True,  by_wins = True)
		daily_goal_rankings = colley.get_rankings_list(all_games, dates, players, is_daily = True,  by_wins = False)
		gamly_win_rankings =  colley.get_rankings_list(all_games, nums,  players, is_daily = False, by_wins = True)
		gamly_goal_rankings = colley.get_rankings_list(all_games, nums,  players, is_daily = False, by_wins = False)

		graphsyousee.create_foosball_graph("Colley Daily Win Rankings",         "Date",        "Ranking", players, dates, daily_win_rankings,  'daily_win_rankings')
		graphsyousee.create_foosball_graph("Colley Daily Goal Rankings",        "Date",        "Ranking", players, dates, daily_goal_rankings, 'daily_goal_rankings')
		graphsyousee.create_foosball_graph("Colley Game by Game Win Rankings",  "Game Number", "Ranking", players, nums,  gamly_win_rankings,  'game_to_game_win_rankings')
		graphsyousee.create_foosball_graph("Colley Game by Game Goal Rankings", "Game Number", "Ranking", players, nums,  gamly_goal_rankings, 'game_by_game_goal_rankings')

		players = {"Caleb", "Will"}
		selected = foosballgame.select_games(all_games, lambda game : game.winner in players and game.loser in players)
		nums = list_nums(selected)
		goal_func = lambda games : list_games(games)
		goal_lists = graphsyousee.get_list_over_range(selected, nums, players, goal_func, is_daily = False)
		graphsyousee.create_foosball_graph("Will Goals On Caleb", "Game Number", "Goals", players, nums, goal_lists, 'will_v_caleb', remove_zeros=False, scatter=True)
