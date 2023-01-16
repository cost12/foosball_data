class Matchup:

	def __init__(self, p1,p2):
		self.player1 = p1
		self.player2 = p2
		self.games = []
		self.p1_wins = 0
		self.p2_wins = 0

	def includes(self, game):
		if game.played_by(self.player1) and game.played_by(self.player2):
			if not game in self.games:
				self.games.append(game)
				self.__update(game)
			return True
		return False

	def add_game(self, game):
		if game.played_by(self.player1) and game.played_by(self.player2):
			if not game in self.games:
				self.games.append(game)
				self.__update(game)

	def __update(self, game):
		if self.player1 == game.winner:
			self.p1_wins += 1
		elif self.player2 == game.winner:
			self.p2_wins += 1
		if self.p2_wins > self.p1_wins:
			self.player1, self.player2 = self.player2, self.player1
			self.p1_wins, self.p2_wins = self.p2_wins, self.p1_wins
