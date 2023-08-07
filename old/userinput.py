from datetime import datetime
import math

import foosballgame
import graphsyousee
import colley
"""
TODO:
 - learn to play Circle Game
 - predicate that allows for selection of a specific matchup of players + color
 - use get_list_over_range to allow for more graph possibilities
 - create lambda functions for get_list_over_range
"""

def print_list(header, games, xfunc, yfunc, line_format, key, reverse=True):
	print(header)
	to_print = []
	for x in xfunc(games):
		y = yfunc(games, x)
		to_print.append([x,y])
	to_print.sort(key=key, reverse=reverse)
	for line in to_print:
		print(line_format(line))

def input_color(text='p1color',default='ANY',default_on_error=True):
	print(text,end=': ')
	col = input().upper()
	if col in {'W','B','ANY'}:
		return col
	elif default_on_error:
		print('default ' + default + ' selected')
		return default
	else:
		return input_color(text,default,default_on_error)

def input_string(text):
	print(text,end=': ')
	return input()

def input_num(text='num',default=0,default_on_error=True):
	print(text,end=': ')
	try:
		return int(input())
	except:
		if default_on_error:
			print('default ' + str(default) + ' selected')
			return default
		else:
			return input_num(text,default,default_on_error)

def input_option(text, options, default=None, default_on_error=True):
	print(text,end=': ')
	op = input()
	if op in options:
		return op
	elif default_on_error:
		if default == None:
			print('default ' + str(options[0]) + ' selected')
			return options[0]
		else:
			print('default ' + str(default) + ' selected')
			return default
	else:
		input_option(text,options,default,default_on_error)

def prepare_sim(games):
	p1 = input_string('player1')
	p2 = input_string('player2')
	p1color = input_color()
	try:
		return p1, p2, foosballgame.goal_prob(games, p1, p2, p1color)
	except ZeroDivisionError:
		print('not enough data to sim, try again')
		return prepare_sim(games)

def interaction(games):
	predicate = foosballgame.FoosballPredicate()
	selected =  foosballgame.select_games(games, predicate.get_predicate())

	print("Welcome, the games have been loaded")
	print("To begin, type a command, to learn more, press i:", end =" ")

	command = input()
	while command != "end":
		if command == 'i':
			print("Commands: \ni - information"
				           +"\nr - reset search"
				           +"\nprint count - print the current number of selected games"
				           +"\nprint games by date - print the count of games on each day"
				           +"\nprint games - print the selected games"
				           +"\nprint streaks - print the longest win/loss and current streak for each player"
				           +"\nprint records - print the records for the players in the selected games"
				           +"\nprint normalized records - print the records as if each player played each other once"
				           +"\nprint goal diffs - print the records for the players in the selected games"
				           +"\nprint avg goals - print the average goals scored for each player"
				           +"\nprint rankings - print colley rankings for players in selected games"
				           +"\nprint win prob - start commands to print win probability"
				           +"\nprint least probable - print the 10 most probable games"
				           +"\nprint most probable - print the 10 most probable games"
				           +"\nwatch game - start watch game commands"
				           +"\nenter game - start commands to enter a game"
				           +"\nsim game - start commands to simulate a hypothetical game"
				           +"\nsim n games - start commands to simulate n hypothetical games"
				           +"\ncreate graph - begin prompts to create a graph"
				           +"\nselect - begin prompts to select game to look at"
				           +"\nend - exit program")
		elif command == 'r':
			predicate.reset()
			selected = foosballgame.select_games(games, predicate.get_predicate())
			print("predicate reset")
		elif command == 'print count':
			print("Games: " + str(len(selected)))
			predicate.print()
		elif command == 'print games by date':
			print_list(  header = "{:<11} {:>5}".format("Date", "Games") \
				       , games = selected \
				       , xfunc = lambda games : foosballgame.get_date_range(games) \
				       , yfunc = lambda games, date : foosballgame.count_games_on_date(games, date) \
				       , line_format = lambda line : "{:<11} {:>5}".format(str(line[0].date()), line[1])
				       , key = lambda line : line[0] \
				       , reverse = False)
		elif command == 'print games':
			print('Games: ' + str(len(selected)))
			for game in selected:
				print(game)
		elif command == 'print streaks':
			consecutive = 'c' == input_option("c for consecutive, a for any streak", ['c','a'], default_on_error=False)
			print_list(  header = "{:<8} {:>3} {:>3} {:>5}".format("Player", "WS", "LS", "NOW") \
				       , games = selected \
				       , xfunc = lambda games : foosballgame.get_player_range(games) \
				       , yfunc = lambda games, player : foosballgame.get_streak(games, player, consecutive) \
				       , line_format = lambda line : "{:<8} {:>3} {:>3} {:>5}".format(line[0], line[1][0], line[1][1], line[1][2][0]+" "+str(line[1][2][1]))
				       , key = lambda line : line[1][0] \
				       , reverse = True)
		elif command == 'print records':
			print_list(  header = "{:<8} {:>3} {:>3}   {:>5}".format("Player", "W", "L", "PCT") \
				       , games = selected \
				       , xfunc = lambda games : foosballgame.get_player_range(games) \
				       , yfunc = lambda games, player : foosballgame.get_record(games, player) \
				       , line_format = lambda line : "{:<8} {:>3} {:>3}   {:.3f}".format(line[0], line[1][0], line[1][1], line[1][0]/float(line[1][0]+line[1][1]))
				       , key = lambda line : line[1][0]/float(line[1][0]+line[1][1]) \
				       , reverse = True)
		elif command == 'print normalized records':
			print_list(  header = "{:<8} {:>5} {:>5}   {:>5}".format("Player", "W", "L", "PCT") \
				       , games = selected \
				       , xfunc = lambda games : foosballgame.get_player_range(games) \
				       , yfunc = lambda games, player : foosballgame.get_normalized_record(games, player) \
				       , line_format = lambda line : "{:<8} {:>5.2f} {:>5.2f}   {:.3f}".format(line[0], line[1][0], line[1][1], line[1][0]/float(line[1][0]+line[1][1]))
				       , key = lambda line : line[1][0]/float(line[1][0]+line[1][1]) \
				       , reverse = True)
		elif command == 'print goal diffs':
			print_list(  header = "{:<8} {:>4} {:>4}   {:>5}".format("Player", "GF", "GA", "PCT") \
				       , games = selected \
				       , xfunc = lambda games : foosballgame.get_player_range(games) \
				       , yfunc = lambda games, player : foosballgame.get_goals_scored(games, player) \
				       , line_format = lambda line : "{:<8} {:>4} {:>4}   {:.3f}".format(line[0], line[1][0], line[1][1], line[1][0]/float(line[1][0]+line[1][1]))
				       , key = lambda line : line[1][0]/float(line[1][0]+line[1][1]) \
				       , reverse = True)
		elif command == 'print avg goals':
			print_list(  header = "{:<8} {:>5}  {:>5}".format("Player", "AVG", "LAVG") \
				       , games = selected \
				       , xfunc = lambda games : foosballgame.get_player_range(games) \
				       , yfunc = lambda games, player : foosballgame.get_average_score(games, player) \
				       , line_format = lambda line : "{:<8} {:.3f}  {:.3f}".format(line[0], line[1][0], line[1][1])
				       , key = lambda line : line[1][0] \
				       , reverse = True)
		elif command == 'print rankings':
			print("w for by wins, g for by goals: ", end = '')
			by_wins = input() == 'w'
			r = colley.get_colley_rankings(selected, by_wins)
			colley.nice_print(r)
		elif command == 'print win prob':
			p1 = input_string('player1')
			p2 = input_string('player2')
			p1color = input_color()
			p1score = input_num('p1 score', default=0)
			p2score = input_num('p2 score', default=0)
			gameto = input_num('to win', default=10)
			print("Probablity p1 wins: %.4f" % foosballgame.get_win_probability(selected, p1, p2, p1color, p1score, p2score, gameto))
		elif command == 'get current win prob':
			pass
		elif command == 'get game prob':
			pass
		elif command == 'print records by color':
			print_list(  header = "{:<8} {} {:>3} {:>3}   {:>5}".format("Player", "C", "W", "L", "PCT") \
				       , games = selected \
				       , xfunc = lambda games : foosballgame.get_player_range(games,and_color=True) \
				       , yfunc = lambda games, player : foosballgame.get_record(games, player[0], color=player[1]) \
				       , line_format = lambda line : "{:<8} {} {:>3} {:>3}   {:.3f}".format(line[0][0], line[0][1], line[1][0], line[1][1], line[1][0]/float(line[1][0]+line[1][1]))
				       , key = lambda line : line[1][0]/float(line[1][0]+line[1][1]) \
				       , reverse = True)
		elif command == 'print expected records':
			print_list(  header = "{:<8} {:>6} {:>6}   {:>5}".format("Player", "EW", "EL", "EPCT") \
				       , games = selected \
				       , xfunc = lambda games : foosballgame.get_player_range(games) \
				       , yfunc = lambda games, player : foosballgame.get_expected_record(games, player) \
				       , line_format = lambda line : "{:<8} {:>6.2f} {:>6.2f}   {:.3f}".format(line[0], line[1][0], line[1][1], line[1][0]/float(line[1][0]+line[1][1]))
				       , key = lambda line : line[1][0]/float(line[1][0]+line[1][1]) \
				       , reverse = True)
		elif command == 'print matchups':
			print_list(  header = "{:<8} {:<8} {:>6} {:>6} {:>6}".format("Player1", "Player2", "P1Wins", "P2Wins", "P1Win%") \
				       , games = selected \
				       , xfunc = lambda games : foosballgame.get_matchups(games) \
				       , yfunc = lambda games, matchup : foosballgame.get_record(matchup.games, matchup.player1) \
				       , line_format = lambda line : "{:<8} {:<8} {:>6} {:>6} {:>6.3f}".format(line[0].player1, line[0].player2, line[1][0], line[1][1], line[1][0]/float(line[1][0]+line[1][1]))
				       , key = lambda line : (line[1][0]/float(line[1][0]+line[1][1]), line[1][0]+line[1][1]) \
				       , reverse = True)
		elif command == 'print least probable':
			or_less_likely_game = "yes" == input_option("consider the probability of more extreme games", ["yes","no"], default="no", default_on_error=True)
			given_total_games_played = "yes" == input_option("consider how many times this matchup occurs", ["yes","no"], default="no", default_on_error=True)
			color_matters = "yes" == input_option("take into account the color played", ["yes","no"], default="yes", default_on_error=True)
			count = input_num("how many",default=10,default_on_error=True)

			probs = []
			for game in selected:
				probs.append([foosballgame.game_probability(selected, game, or_less_likely_game,given_total_games_played,color_matters), game])
			probs.sort(key = lambda x : x[0], reverse=False)
			for i in range(0,count):
				print("{:>3}. Prob: {:>7.3f} %: {}".format(i+1, 100*probs[i][0], probs[i][1]))
		elif command == 'print most probable':
			or_less_likely_game = "yes" == input_option("consider the probability of more extreme games", ["yes","no"], default="no", default_on_error=True)
			given_total_games_played = "yes" == input_option("consider how many times this matchup occurs", ["yes","no"], default="no", default_on_error=True)
			color_matters = "yes" == input_option("take into account the color played", ["yes","no"], default="yes", default_on_error=True)
			count = input_num("how many",default=10,default_on_error=True)

			probs = []
			for game in selected:
				probs.append([foosballgame.game_probability(selected, game, or_less_likely_game,given_total_games_played,color_matters), game])
			probs.sort(key = lambda x : x[0], reverse=True)
			for i in range(0,count):
				print("{:>3}. Prob: {:>7.3f} %: {}".format(i+1, 100*probs[i][0], probs[i][1]))
		elif command == 'sim game':
			p1, p2, p1_prob = prepare_sim(selected)
			digits = 2
			sim = True
			while sim:
				p1_score, p2_score = foosballgame.simulate_game(p1_prob, p1_score=0, p2_score=0, gameto=10)
				print((p1 + " {0:>{1}} " + p2 + " {2:>{3}}, enter to sim, e to exit: ").format(p1_score,digits,p2_score,digits),end='')
				sim = input() == ''
		elif command == 'sim n games':
			p1, p2, p1_prob = prepare_sim(selected)
			n = input_num('n',1)
			digits = math.ceil(math.log10(n))+1
			sim = True
			while sim:
				p1_wins = 0
				p2_wins = 0
				for i in range(0,n):
					p1_score, p2_score = foosballgame.simulate_game(p1_prob, p1_score=0, p2_score=0, gameto=10)
					if p1_score > p2_score:
						p1_wins += 1
					else:
						p2_wins += 1
				print((p1 + " {0:>{1}} " + p2 + " {2:>{3}}, enter to sim, e to exit: ").format(p1_wins,digits,p2_wins,digits),end='')
				sim = input() == ''
		elif command == 'create graph':
			is_daily = 'd' == input_option('d for daily, g for by game',['d','g'], default_on_error=False)
			if is_daily:
				xlist = foosballgame.get_date_range(selected)
			else:
				xlist = foosballgame.get_num_range(selected)
			selection = 'o'
			while (selection == 'o'):
				if is_daily:
					selection = input_option('select y-axis values, o for options', ['o','wr','gr','w','l','gf','ga','w%','g%','wp','gp','ag','agl','aga','ws','ls','gbd'], default_on_error=False)
				else:
					selection = input_option('select y-axis values, o for options', ['o','wr','gr','w','l','gf','ga','w%','g%','wp','gp','ag','agl','aga','ws','ls'], default_on_error=False)
				if selection == 'o':
					print('Options: \no   - options' \
						          +'\nwr  - win rankings' \
						          +'\ngr  - goal rankings' \
						          +'\nw   - wins' \
						          +'\nl   - losses' \
						          +'\ngf  - goals for' \
						          +'\nga  - goals against' \
						          +'\nw%  - win percentage' \
						          +'\ng%  - goal percentage' \
						          +'\nwp  - win probability' \
						          +'\ngp  - goal probability' \
						          +'\nag  - average goals scored' \
						          +'\nagl - average goals score in a loss' \
						          +'\naga - average goals allowed' \
						          +'\nws  - current win streak' \
						          +'\nls  - current loss streak' \
						          +'\ngbd - games by date\n')
			y_funcs = {'wr': lambda games : colley.get_colley_rankings(games, by_wins = True),
			           'gr': lambda games : colley.get_colley_rankings(games, by_wins = False),
			           'w':  lambda games : foosballgame.get_records(games),
			           'l':  lambda games : foosballgame.get_records(games),
			           'gf': lambda games : foosballgame.get_goals_scored_for_all(games),
			           'ga': lambda games : foosballgame.get_goals_scored_for_all(games),
			           'w%': lambda games : foosballgame.get_records(games),
			           'g%': lambda games : foosballgame.get_goals_scored_for_all(games), 
			           'wp': lambda games : foosballgame.get_win_probabilities(games),
			           'gp': lambda games : foosballgame.goal_probs(games),
			           'ag': lambda games : foosballgame.get_average_scores(games), 
			           'agl':lambda games : foosballgame.get_average_scores(games), 
			           'aga':lambda games : foosballgame.get_average_scores_allowed(games), 
			           'ws': lambda games : foosballgame.get_streaks(games),
			           'ls': lambda games : foosballgame.get_streaks(games) }
			identity = lambda x : x
			first =    lambda x : x[0]
			second =   lambda x : x[1]
			modifiers = {'wr': identity,
			             'gr': identity,
			             'w':  first, 
			             'l':  second,
			             'gf': first,
			             'ga': second,
			             'w%': lambda x : x[0]/float(x[0]+x[1]),
			             'g%': lambda x : x[0]/float(x[0]+x[1]),
			             'wp': identity,
			             'gp': identity,
			             'ag': first,
			             'agl':second,
			             'aga':first,
			             'ws': lambda x : x['win'],
			             'ls': lambda x : x['loss'] }
			players = foosballgame.get_player_range(selected)
			ignore = []
			ignore_loop = True
			while(ignore_loop):
				pignore = input_string('player to not graph')
				if pignore in players:
					ignore.append(pignore)
				else:
					ignore_loop = False
			remove_zeros = 'yes' == input_option('remove zeros, yes or no', ['yes','no'],default='yes',default_on_error=True)
			if selection == 'gbd':
				remove_zeros = False
				players = ['Games']
				ylist = {'Games':[]}
				for date in xlist:
					ylist['Games'].append(foosballgame.count_games_on_date(selected, date))
			else:
				ylist = graphsyousee.get_list_over_range(selected, xlist, players, y_funcs[selection], is_daily, modifiers[selection])

			name = input_string('name the graph')
			xlabel = input_string('label the x axis')
			ylabel = input_string('label the y axis')
			filename = input_string('name the file')
			graphsyousee.create_foosball_graph(name, xlabel, ylabel, players, xlist, ylist, filename, remove_zeros, ignore)
		elif command == 'select matchup':
			p1 = input_string("choose player 1")
			p2 = input_string("choose player 2")
			selected = foosballgame.select_games(foosballgame.get_matchup(games, p1, p2).games, predicate.get_predicate())
		elif command == 'select':
			print("select for what? (i for info): ", end = '')
			comm2 = input()
			if comm2 == 'i':
				print("Select Commands: \ni - information" \
					                  +"\nplayer - select a player in games" \
					                  +"\nwinner - select a player as a winner" \
					                  +"\nloser - select a player as a loser" \
					                  +"\nexcept player - exclude results with player" \
					                  +"\nexcept winner - exclude player as winner" \
					                  +"\nexcept loser - exclude player as loser" \
					                  +"\nset loss min - set minimum score for a loss" \
					                  +"\nset loss max - set the max score for a loss" \
					                  +"\nset winner color - games with winner as color" \
					                  +"\nset number min - set the min number game" \
					                  +"\nset number max - set the max number game" \
					                  +"\nset date min - set the min date" \
					                  +"\nset date max - set the max date\n")
				print("which command: ", end = '')
				comm2 = input()
			if comm2 == 'player':
				print("which player: ", end = '')
				player = input()
				predicate.winners.remove("ANY")
				predicate.losers.remove("ANY")
				predicate.winners.add(player)
				predicate.losers.add(player)
			elif comm2 == 'winner':
				print("which player: ", end = '')
				player = input()
				predicate.winners.remove("ANY")
				predicate.losers.remove("ANY")
				predicate.winners.add(player)
			elif comm2 == 'loser':
				print("which player: ", end = '')
				player = input()
				predicate.winners.remove("ANY")
				predicate.losers.remove("ANY")
				predicate.losers.add(player)
			elif comm2 == 'except player':
				print("which player: ", end = '')
				player = input()
				predicate.exclude_winners.add(player)
				predicate.exclude_losers.add(player)
			elif comm2 == 'except winner':
				print("which player: ", end = '')
				player = input()
				predicate.exclude_winners.add(player)
			elif comm2 == 'except loser':
				print("which player: ", end = '')
				player = input()
				predicate.exclude_losers.add(player)
			elif comm2 == 'set loss min':
				print("choose value: ", end = '')
				num = int(input())
				predicate.lose_score_min = num
			elif comm2 == 'set loss max':
				print("choose value: ", end = '')
				num = int(input())
				predicate.lose_score_max = num
			elif comm2 == 'set winner color':
				print("choose value: ", end = '')
				col = input().upper()
				predicate.winner_color = col
			elif comm2 == 'set number min':
				print("choose value: ", end = '')
				num = int(input())
				predicate.number_min = num
			elif comm2 == 'set number max':
				print("choose value: ", end = '')
				num = int(input())
				predicate.number_max = num
			elif comm2 == 'set date min':
				print("year: ", end = '')
				y = int(input())
				print("month: ", end = '')
				m = int(input())
				print("day: ", end = '')
				d = int(input())
				predicate.date_min = datetime(y,m,d)
			elif comm2 == 'set date max':
				print("year: ", end = '')
				y = int(input())
				print("month: ", end = '')
				m = int(input())
				print("day: ", end = '')
				d = int(input())
				predicate.date_max = datetime(y,m,d)
			else:
				print("invalid command")
			selected = foosballgame.select_games(games, predicate.get_predicate())
		else:
			print("Unknown command, press i for more commands")
		print("")
		print("new command:", end =" ")
		command = input()

	print("The end, goodbye")