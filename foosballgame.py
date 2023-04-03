import matchup

import datetime
import pandas as pd
import math
import random

class FoosballGame:

	def __init__(self, w, l, ws, ls, wc, d, n):
		self.winner = w
		self.loser = l
		self.winner_score = ws
		self.loser_score = ls
		self.winner_color = wc
		self.date = d
		self.number = n

	def played_by(self, player):
		return player in {self.winner, self.loser}

	def player_goals(self, player):
		if player == self.winner:
			return self.winner_score
		elif player == self.loser:
			return self.loser_score
		else:
			return 0

	def player_color(self, player):
		if player == self.winner:
			return self.winner_color
		elif player == self.loser:
			return self.loser_color()
		else:
			return None

	def loser_color(self):
		if self.winner_color == 'B':
			return 'W'
		else:
			return 'B'

	def __repr__(self):
		return "{:<8} {:>2} {:<8} {:>2}    {:>4} On: {:>10}, WC: {})".format( self.winner,  \
			                                                      self.winner_score, \
		                                                          self.loser, \
		                                                          self.loser_score,  \
		                                                          '(' + str(self.number), \
		                                                          str(self.date.strftime("%m/%d/%Y")), \
		                                                          self.winner_color)

	def __str__(self):
		return "{:<8} {:>2} {:<8} {:>2}    {:>4} On: {:>10}, WC: {})".format( self.winner,  \
			                                                      self.winner_score, \
		                                                          self.loser, \
		                                                          self.loser_score,  \
		                                                          '(' + str(self.number), \
		                                                          str(self.date.strftime("%m/%d/%Y")), \
		                                                          self.winner_color)

def get_record(games, p1, color='ANY'):
	wins = 0
	losses = 0
	for game in games:
		if game.winner == p1 and (color == 'ANY' or game.winner_color == color):
			wins += 1
		elif game.loser == p1 and (color == 'ANY' or game.loser_color() == color):
			losses += 1
	return wins, losses

def get_expected_record(games, p1):
	game_count = 0
	gf = 0
	ga = 0
	for game in games:
		if game.winner == p1:
			gf += game.winner_score
			ga += game.loser_score
			game_count += 1
		elif game.loser == p1:
			ga += game.winner_score
			gf += game.loser_score
			game_count += 1
	pct = get_win_prob(gf/float(gf+ga))
	return game_count*pct, game_count*(1-pct)

def get_records(games):
	records = {}
	for game in games:
		if not game.winner in records.keys():
			records[game.winner] = [1,0]
		else:
			records[game.winner][0] += 1
		if not game.loser in records.keys():
			records[game.loser] = [0,1]
		else:
			records[game.loser][1] += 1
	return records

def get_matchup(games, p1, p2):
	m = matchup.Matchup(p1,p2)
	for game in games:
		m.add_game(game)
	return m

def get_matchups(games):
	matchups = []
	for game in games:
		added = False
		for m in matchups:
			if m.includes(game):
				added = True
				break
		if not added:
			m2 = matchup.Matchup(game.winner,game.loser)
			m2.add_game(game)
			matchups.append(m2)
	return matchups

def get_normalized_record(games, p1):
	opponent_records = {}
	for game in games:
		if game.winner == p1:
			if game.loser in opponent_records:
				opponent_records[game.loser][0] += 1
			else:
				opponent_records[game.loser] = [1,0]
		elif game.loser == p1:
			if game.winner in opponent_records:
				opponent_records[game.winner][1] += 1
			else:
				opponent_records[game.winner] = [0,1]
	wins = 0
	losses = 0
	for opp in opponent_records.keys():
		wins +=   opponent_records[opp][0]/(opponent_records[opp][0]+opponent_records[opp][1])
		losses += opponent_records[opp][1]/(opponent_records[opp][0]+opponent_records[opp][1])
	return wins, losses

def get_streak(games, p1, consecutive=False):
	max_win = 0
	max_loss = 0
	win = 0
	loss = 0
	for game in games:
		if game.winner == p1:
			win += 1
			loss = 0
		elif game.loser == p1:
			win = 0
			loss += 1
		elif consecutive:
			win = 0
			loss = 0
		if win > max_win:
			max_win = win
		if loss > max_loss:
			max_loss = loss
	current = ("W",win)
	if loss > 0:
		current = ("L",loss)
	return max_win, max_loss, current

def get_streaks(games):
	substreaks = {}
	for game in games:
		if not game.winner in substreaks.keys():
			substreaks[game.winner] = {'maxwin':1,'maxloss':0,'win':1,'loss':0}
		else:
			substreaks[game.winner]['win'] += 1
			substreaks[game.winner]['loss'] = 0
			if substreaks[game.winner]['win'] > substreaks[game.winner]['maxwin']:
				substreaks[game.winner]['maxwin'] = substreaks[game.winner]['win']
		if not game.loser in substreaks.keys():
			substreaks[game.loser] = {'maxwin':0,'maxloss':1,'win':0,'loss':1}
		else:
			substreaks[game.loser]['loss'] += 1
			substreaks[game.loser]['win'] = 0
			if substreaks[game.loser]['loss'] > substreaks[game.loser]['maxloss']:
				substreaks[game.loser]['maxloss'] = substreaks[game.loser]['loss']
	return substreaks

def count_games_on_date(games, date):
	count = 0
	for game in games:
		if game.date == date:
			count += 1
	return count

def get_average_score(games, p1):
	tot = 0
	g = 0
	loss_t = 0
	l_g = 0
	for game in games:
		if game.winner == p1:
			tot += game.winner_score
			g += 1
		elif game.loser == p1:
			tot += game.loser_score
			g += 1
			loss_t += game.loser_score
			l_g += 1
	return div(tot, g), div(loss_t, l_g)

def get_average_scores(games):
	avgs = {}
	totals = {}
	for game in games:
		if not game.winner in totals.keys():
			#                      goals, games, goals in losses, losses
			totals[game.winner] = [game.winner_score, 1, 0,0]
		else:
			totals[game.winner][0] += game.winner_score
			totals[game.winner][1] += 1
		if not game.loser in totals.keys():
			totals[game.loser] = [game.loser_score, 1, game.loser_score, 1]
		else:
			totals[game.loser][0] += game.loser_score
			totals[game.loser][1] += 1
			totals[game.loser][2] += game.loser_score
			totals[game.loser][3] += 1
	for player in totals.keys():
		avgs[player] = [div(totals[player][0], totals[player][1]), div(totals[player][2], totals[player][3])]
	return avgs

def get_average_scores_allowed(games):
	avgs = {}
	totals = {}
	for game in games:
		if not game.loser in totals.keys():
			#                     ga, games, goals wins, wins
			totals[game.loser] = [game.winner_score, 1, 0,0]
		else:
			totals[game.loser][0] += game.winner_score
			totals[game.loser][1] += 1
		if not game.winner in totals.keys():
			totals[game.winner] = [game.loser_score, 1, game.loser_score, 1]
		else:
			totals[game.winner][0] += game.loser_score
			totals[game.winner][1] += 1
			totals[game.winner][2] += game.loser_score
			totals[game.winner][3] += 1
	for player in totals.keys():
		avgs[player] = [div(totals[player][0], totals[player][1]), div(totals[player][2], totals[player][3])]
	return avgs


def div(a,b,val=0):
	if b == 0:
		return val
	return float(a)/b

def get_goals_scored(games, p1):
	goals_for = 0
	goals_against = 0
	for game in games:
		if game.winner == p1:
			goals_for += game.winner_score
			goals_against += game.loser_score
		elif game.loser == p1:
			goals_for += game.loser_score
			goals_against += game.winner_score
	return goals_for, goals_against

def get_goals_scored_for_all(games):
	goals = {}
	for game in games:
		if not game.winner in goals.keys():
			goals[game.winner] = [game.winner_score,game.loser_score]
		else:
			goals[game.winner][0] += game.winner_score
			goals[game.winner][1] += game.loser_score
		if not game.loser in goals.keys():
			goals[game.loser] = [game.loser_score,game.winner_score]
		else:
			goals[game.loser][0] += game.loser_score
			goals[game.loser][1] += game.winner_score
	return goals

def select_games(games, predicate):
	selected = []
	for game in games:
		if (predicate(game)):
			selected.append(game)
	return selected

def get_date_range(games):
	min_date = datetime.date(9000, 1, 1)
	max_date = datetime.date(2000, 1, 1)
	for game in games:
		if game.date < min_date:
			min_date = game.date
		if game.date > max_date:
			max_date = game.date
	return pd.date_range(min_date,max_date,freq='d')

def get_num_range(games):
	min_num = 0
	max_num = 0
	for game in games:
		if game.number < min_num:
			min_num = game.number
		if game.number > max_num:
			max_num = game.number
	return range(min_num, max_num+1)

def get_player_range(games, and_color=False):
	players = set()
	for game in games:
		if and_color:
			players.add((game.winner, game.winner_color))
			players.add((game.loser, game.loser_color()))
		else:
			players.add(game.winner)
			players.add(game.loser)
	return players

def game_probability(games, game, or_less_likely_game=False,given_total_games_played=False,color_matters=True):
	if color_matters:
		p1prob = goal_prob(games, game.winner, game.loser, "ANY")
	else:
		p1prob = goal_prob(games, game.winner, game.loser, game.winner_color)
	if given_total_games_played:
		games_played = 0
		for g in games:
			if g.winner == game.winner and g.loser == game.loser and (g.player_color(game.winner) == game.winner_color or not color_matters):
				games_played += 1
	return game_prob(p1prob, game, or_less_likely_game, games_played, given_total_games_played)

def game_prob(p1_goal_prob, game, or_less_likely_game=False, games_played=1, given_total_games_played=False):
	g_prob = p1_goal_prob**(game.winner_score-1) * (1-p1_goal_prob)**game.loser_score * math.comb(game.winner_score-1+game.loser_score,game.loser_score ) * p1_goal_prob
	
	less_likely_prob = 0
	if or_less_likely_game:
		for i in range(0,game.loser_score):
			less_likely_prob += p1_goal_prob**(game.winner_score-1) * (1-p1_goal_prob)**i * math.comb(game.winner_score-1+i,i ) * p1_goal_prob
		g_prob = min(g_prob+less_likely_prob, 1-less_likely_prob)

	if given_total_games_played:
		g_prob = 1-((1-g_prob)**games_played)
	return g_prob

def goal_prob(games, p1, p2, p1color="ANY"):
	p1_goals = 1
	p2_goals = 1
	for game in games:
		if game.winner == p1 and game.loser == p2 and (p1color=="ANY" or p1color == game.winner_color):
			p1_goals += game.winner_score
			p2_goals += game.loser_score
		elif game.winner == p2 and game.loser == p1 and (p1color=="ANY" or p1color == game.loser_color()):
			p1_goals += game.loser_score
			p2_goals += game.winner_score
	return p1_goals/float(p1_goals+p2_goals)

def goal_probs(games):
	goals = get_goals_scored_for_all(games)
	probs = {}
	for player in goals.keys():
		probs[player] = (goals[player][0]+1)/float(goals[player][0]+goals[player][1]+2)
	return probs

def simulate_game(p1_prob, p1_score=0, p2_score=0, gameto=10):
	while p1_score < gameto and p2_score < gameto:
		rand = random.random()
		if rand < p1_prob:
			p1_score += 1
		else:
			p2_score += 1
	return p1_score, p2_score

def get_win_probability(games, p1, p2, p1color="ANY", p1score=0, p2score=0, gameto=10):
	p1_goal_prob = goal_prob(games, p1, p2, p1color)

	return get_win_prob(p1_goal_prob, p1score,p2score,gameto)

def get_win_prob(p1goalprob, p1score=0,p2score=0,gameto=10):
	if p1score >= gameto:
		return 1
	if p2score >= gameto:
		return 0
	p2goalprob = 1 - p1goalprob
	p1_left = gameto-p1score
	p2_left = gameto-p2score

	probability_p2_loses = 0
	for x in range(0,p2_left):
		probability_p2_loses += p1goalprob**(p1_left-1) * p2goalprob**x * math.comb(p1_left-1+x,x) * p1goalprob
	return probability_p2_loses

def get_win_probabilities(games, p1score=0,p2score=0,gameto=10):
	goal_probs = goal_probs(games)
	win_probs = {}
	for player in goal_probs.keys():
		win_probs[player] = get_win_prob(goal_probs[player], p1score,p2score,gameto)
	return win_probs

def get_prob_of_score(goalprob,score,cur_score=0,opp_score=0,gameto=10):
	if score < cur_score or score > gameto:
		return 0.0
	if score == gameto:
		return get_win_prob(goalprob,cur_score,opp_score,gameto)
	if opp_score == gameto:
		return score == cur_score
	to_go = score - cur_score
	opp_to_go = gameto-opp_score
	opp_goal_prob = 1-goalprob
	prob = goalprob**to_go * opp_goal_prob**(opp_to_go-1) * math.comb(to_go+opp_to_go-1,to_go) * opp_goal_prob
	return prob



class FoosballPredicate:

	def __init__(self):
		self.reset()

	def reset(self):
		self.winners = {"ANY"}
		self.losers =  {"ANY"}

		self.exclude_winners = set()
		self.exclude_losers =  set()

		self.win_score_max = 10
		self.win_score_min = 10

		self.lose_score_max = 9
		self.lose_score_min = 0

		self.winner_color = 'ANY'

		self.number_min = 0
		self.number_max = 999999

		self.date_min = datetime.date(2000, 1, 1)
		self.date_max = datetime.date(9000, 1, 1)

	def get_predicate(self):
		return lambda game : self.predicate(game)

	def print(self):
		print("Selecting for:")
		print("Winners: " + str(self.winners))
		print("Losers: " + str(self.losers))
		print("Exclude winners: " + str(self.exclude_winners))
		print("Exclude losers: " + str(self.exclude_losers))
		print("Lose score from: " + str(self.lose_score_min) + " to " + str(self.lose_score_max))
		print("Winner color: " + str(self.winner_color))
		print("Number from: " + str(self.number_min) + " to " + str(self.number_max))
		print("Date from: " + str(self.date_min) + " to " + str(self.date_max))

	def predicate(self, game):
		return ((game.winner in self.winners or "ANY" in self.winners) or \
		        (game.loser  in self.losers  or "ANY" in self.losers)) and \
		       (game.winner not in self.exclude_winners) and \
		       (game.loser  not in self.exclude_losers) and \
		       game.winner_score <= self.win_score_max and \
		       game.winner_score >= self.win_score_min and \
		       game.loser_score  <= self.lose_score_max and \
		       game.loser_score  >= self.lose_score_min and \
		       (game.winner_color == self.winner_color or self.winner_color == 'ANY') and \
		       game.number <= self.number_max and \
		       game.number >= self.number_min and \
		       game.date <= self.date_max and \
		       game.date >= self.date_min
