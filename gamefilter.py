import datetime

import event_date
import foosballgame

"""
Acts as a predicate to filter a list of games so only ones with desired attributes remain
"""
class GameFilter:
	
	def __init__(self) -> None:
		self.reset()

	"""
	Resets the filter to its initial state or initializes the filter
	"""
	def reset(self) -> None:
		self.winners = {"ANY"}
		self.losers =  {"ANY"}

		self.win_score_max = 10
		self.win_score_min = 10

		self.lose_score_max = 9
		self.lose_score_min = 0

		self.winner_color = 'ANY'

		self.number_min = 0
		self.number_max = 999999

		self.date_ranges = [event_date.EventDate("All",self.start_date(),self.end_date())]
	
	"""
	Early date that all games will be later than
	"""
	def start_date(self) -> datetime.date:
		return datetime.date(2000, 1, 1)

	"""
	Late date that all games will be before
	"""
	def end_date(self) -> datetime.date:
		return datetime.date(9000, 1, 1)

	"""
	Returns the predicate as a lambda
	"""
	def get_predicate(self): # TODO: figure out how to type hint this
		return lambda game : self.predicate(game)
	
	"""
	Filters a list of games into a new list of games that match the predicate
	"""
	def filter_games(self, games:list[foosballgame.FoosballGame]) -> list[foosballgame.FoosballGame]:
		new_lis = []
		for game in games:
			if self.predicate(game):
				new_lis.append(game)
		return new_lis

	"""
	Determines wether a game matches the criteria or not
	"""
	def predicate(self, game:foosballgame.FoosballGame) -> bool:
		in_dates = False
		for event in self.date_ranges:
			if event.contains_date(game.date):
				in_dates = True
		return ((game.winner in self.winners or "ANY" in self.winners) and \
		        (game.loser  in self.losers  or "ANY" in self.losers)) and \
		       game.winner_score <= self.win_score_max and \
		       game.winner_score >= self.win_score_min and \
		       game.loser_score  <= self.lose_score_max and \
		       game.loser_score  >= self.lose_score_min and \
		       (game.winner_color == self.winner_color or self.winner_color == 'ANY') and \
		       game.number <= self.number_max and \
		       game.number >= self.number_min and \
		       in_dates

	"""
	Prints out the predicate for the command line one
	"""
	def print(self) -> None:
		print("Selecting for:")
		print("Winners: " + str(self.winners))
		print("Losers: " + str(self.losers))
		print("Lose score from: " + str(self.lose_score_min) + " to " + str(self.lose_score_max))
		print("Winner color: " + str(self.winner_color))
		print("Number from: " + str(self.number_min) + " to " + str(self.number_max))
		print("Date in: " + str(self.date_ranges))