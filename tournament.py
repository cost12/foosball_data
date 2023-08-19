import random

import statcollector as sc
import foosballgame

class Tournament:
    """
    Tournament Styles to consider:
    - random seed
    - ranked seed

    - single elimination
    - double elimination
    - best of 2k+1/ first to k+1
    - round robin

    - round reseeding
    - fixed bracket
    """
    # TODO: enum?
    RANDOM_SEEDING = 0
    SKILL_SEEDING = 1
    AS_ENTERTED_SEEDING = 2
    SEEDING = {'random':RANDOM_SEEDING,'skill':SKILL_SEEDING,'as entered':AS_ENTERTED_SEEDING}

    SINGLE_ELIMINATION = 0
    DOUBLE_ELIMINATION = 1
    ROUND_ROBIN = 2
    TYPE = {'single elimination':SINGLE_ELIMINATION, 'double elimination':DOUBLE_ELIMINATION, 'round robin':ROUND_ROBIN}

    def __init__(self, id, players:list[str]=None, tournament_type:int=0, seeding:int=0, reseeding:bool=False):
        if players is None:
            self.players = list[str]()
        else:
            self.players = players

        self.started = False
        self.type = tournament_type
        self.seeding = seeding
        self.reseeding = reseeding

        self.round_results = list[TournamentRound]()

        self.stats = None
        self.attached = False
        self.started = False

        self.listeners = []
        self.id = id

        self.seed_players()

    def begin(self) -> bool:
        if self.type == self.DOUBLE_ELIMINATION or self.type == self.ROUND_ROBIN:
            return False
        if not self.started:
            self.started = True
            round = TournamentRound(0,self.players,self.type,True)
            round.add_listener(self)
            self.round_results.append(round)
            return True
        return False
    
    def advance(self) -> bool:
        if self.started:
            if self.round_results[-1].is_over():
                if not self.is_over():
                    id = len(self.round_results)
                    round = TournamentRound(id,self.players,self.type,self.reseeding,self.round_results[-1].advancers())
                    round.add_listener(self)
                    self.round_results.append(round)
                    return True
        return False
    
    def update_round(self, id):
        if self.round_over():
            self.notify_listeners()

    def add_listener(self, listener):
        self.listeners.append(listener)

    def remove_listener(self, listener):
        self.listeners.remove(listener)

    def notify_listeners(self):
        for listener in self.listeners:
            listener.update_tournament(self.id)
    
    def winner(self):
        if self.is_over():
            return self.round_results[-1].advancers()[0]

    def is_over(self):
        return self.started and self.round_results[-1].is_over() and len(self.round_results[-1].advancers()) <= 1
    
    def round_over(self) -> bool:
        return self.round_results[-1].is_over()

    def sim_round(self) -> bool:
        pass

    def add_game(self, game:foosballgame.FoosballGame) -> None:
        pass

    def seed_players(self) -> None:
        if not self.started:
            if self.seeding == self.RANDOM_SEEDING:
                random.shuffle(self.players)
            elif self.seeding == self.SKILL_SEEDING:
                if self.attached:
                    self.players.sort(key=lambda player: self.stats.skill_tracker.get_rating(player), reverse=True)

    def list_games(self, round:int=None) -> list[foosballgame.FoosballMatchup]:
        pass

    def add_player(self, player:str) -> None:
        if not self.started:
            self.players.append(player)
            self.seed_players()

    def add_players(self, players:list[str]) -> None:
        if not self.started:
            self.players.extend(players)
            self.seed_players()

    def remove_player(self, player:str):
        if not self.started:
            if player in self.players:
                self.players.remove(player)

    def remove_players(self, players:list[str]):
        if not self.started:
            for player in players:
                if player in self.players:
                    self.players.remove(player)

    def set_players(self, players:list[str]) -> None:
        if not self.started:
            self.players.clear()
            self.players.extend(players)
            self.seed_players()

    def set_seeding(self, seeding:list[str]) -> None:
        if not self.started:
            self.players.clear()
            self.players.extend(seeding)
            self.seeding = self.AS_ENTERTED_SEEDING

    def set_seed(self, player:str, seed:int):
        if not self.started:
            if player in self.players:
                self.players.remove(player)
            self.players.insert(seed,player)
            self.seeding = self.AS_ENTERTED_SEEDING

    def get_win_odds(self, player:str) -> float:
        pass

    def get_performance(self, player:str) -> any:
        pass

    def attach(self, stats:sc.StatCollector) -> None:
        if not self.attached:
            self.stats = stats
            self.attached = True
            if self.seeding == self.SKILL_SEEDING:
                self.seed_players()

    def detach(self) -> None:
        self.stats = None
        self.attached = False

class TournamentRound:

    def __init__(self, id, seeded_players:list[str], round_type:int, reseeding:bool, prev_winners:list[str]=None):
        assert prev_winners is None or set(prev_winners).issubset(seeded_players)
        assert prev_winners is None or len(prev_winners) > 0
        assert len(seeded_players) > 0
        
        self.seeded_players = seeded_players

        if prev_winners is None:
            self.round_players = list(self.seeded_players)
        else:
            self.round_players = prev_winners
        self.bye_players = []

        self.started = False
        self.type = round_type
        self.reseeding = reseeding
       
        self.matchups = list[foosballgame.FoosballMatchup]()
        self.attached = False
        self.stats = None
        self.listeners = []
        self.id = id
        self.set_matchups()

    def add_listener(self, listener):
        self.listeners.append(listener)

    def notify_listeners(self):
        for listener in self.listeners:
            listener.update_round(self.id)

    def set_matchups(self):
        if not self.type == Tournament.SINGLE_ELIMINATION:
            return
        num_players = len(self.round_players)
        pow_2 = 1
        while((pow_2 << 1) < num_players):
            pow_2 = pow_2 << 1
        num_to_eliminate = num_players - pow_2
        num_round = 2*num_to_eliminate
        if self.reseeding:
            self.round_players.sort(key=lambda p: self.seeded_players.index(p))
            start = num_players - num_round
            for i in range(num_round//2):
                matchup = foosballgame.FoosballMatchup(self.round_players[start+i],self.round_players[-(i+1)],i)
                matchup.add_listener(self)
                self.matchups.insert((i+1)//2,matchup)
        else:
            start = num_players - num_round
            for i in range(0,num_round,2):
                matchup = foosballgame.FoosballMatchup(self.round_players[start+i],self.round_players[start+i+1],i//2)
                matchup.add_listener(self)
                self.matchups.append(matchup)
        self.bye_players = list(self.round_players[0:start])
        
    def update_matchup(self, id):
        if self.is_over():
            self.notify_listeners()

    def is_over(self) -> bool:
        for matchup in self.matchups:
            if not matchup.is_over():
                return False
        return True
    
    def advancers(self) -> list[str]:
        advancers = list[str]()
        advancers.extend(self.bye_players)
        for matchup in self.matchups:
            if matchup.is_over():
                advancers.append(matchup.winner())
        return advancers
    
    def winners(self) -> list[str]:
        winners = list[str]()
        for matchup in self.matchups:
            if matchup.is_over():
                winners.append(matchup.winner())
        return winners
    
    def losers(self) -> list[str]:
        losers = list[str]()
        for matchup in self.matchups:
            if matchup.is_over():
                losers.append(matchup.loser())
        return losers

    def attach(self,stats:sc.StatCollector) -> bool:
        if not self.attached:
            self.attached = True
            self.stats = stats
            return True
        return False

    def detach(self) -> None:
        self.stats = None
        self.attached = False