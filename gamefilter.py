import datetime

import event_date
import foosballgame

"""
Acts as a predicate to filter a list of games so only ones with desired attributes remain
"""
class GameFilter:

	RESTRICTED = 0            # select only games that have winner in winners AND loser in losers
	OPEN = 1                  # select pnly games that have winner in winners OR loser in losers
	SINGLE = 2                # select only games that have player in winners OR player in losers where player plays as winner color
							  # (only works when only one player is selected)
	STRS = ['restricted', 'open', 'single']

	@staticmethod
	def str_to_select(s:str):
		s = s.lower()
		return GameFilter.STRS.index(s)
		
	@staticmethod
	def select_to_str(n:int):
		return GameFilter.STRS[n]

	def __init__(self) -> None:
		self.reset()

	"""
	Resets the filter to its initial state or initializes the filter
	"""
	def reset(self) -> None:
		self.initialized = False
		self.winners = set()
		self.losers =  set()
		self.select_type = GameFilter.RESTRICTED

		self.win_score_max = 10
		self.win_score_min = 1

		self.lose_score_max = 9
		self.lose_score_min = 0

		self.winner_color = ['B','W']

		self.number_min = 0
		self.number_max = 999999

		self.date_ranges = list[event_date.EventDate]() #[event_date.EventDate("All",self.start_date(),self.end_date())]
		self.days_of_week = [0,1,2,3,4,5,6]
	
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
		if not in_dates:
			return False
		if self.select_type == GameFilter.RESTRICTED: # changes whether or or and
			if not (((game.winner in self.winners or "ANY" in self.winners) and \
		             (game.loser  in self.losers  or "ANY" in self.losers)) and \
		       		game.winner_color in self.winner_color):
				return False
		elif self.select_type == GameFilter.OPEN:
			if not (((game.winner in self.winners or "ANY" in self.winners) or \
		             (game.loser  in self.losers  or "ANY" in self.losers)) and \
		       		game.winner_color in self.winner_color):
				return False
		else:
			if not ((game.winner in self.winners and game.winner_color in self.winner_color) or \
		            (game.loser  in self.losers and game.loser_color() in self.winner_color)):
				return False
		return game.winner_score <= self.win_score_max and \
		       game.winner_score >= self.win_score_min and \
		       game.loser_score  <= self.lose_score_max and \
		       game.loser_score  >= self.lose_score_min and \
		       game.number <= self.number_max and \
		       game.number >= self.number_min and \
		       game.date.weekday() in self.days_of_week

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