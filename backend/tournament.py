import random
from enum import Enum, auto
import logging

from backend import statcollector
from backend import foosballgame
from backend import gamefilter

logger = logging.getLogger(__name__)

class TournamentSeeding(Enum):
    RANDOM = auto()
    SKILL = auto()
    AS_ENTERED = auto()

class TournamentElimination(Enum):
    SINGLE = auto()
    DOUBLE = auto()
    ROUND_ROBIN = auto()
    WORLD_CUP = auto()

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

    def __init__(
        self,
        tournament_id,
        players:list[str]=None,
        tournament_type:int=0,
        seeding:int=0,
        reseeding:bool=False,
        num_groups:int=1,
        rr_num_advance:int=1
    ):
        if players is None:
            self.players = list[str]()
        else:
            self.players = players

        self.groups = list[list[str]]()
        for _ in range(num_groups):
            self.groups.append(list[str])

        self.started = False
        self.type = tournament_type
        self.seeding = seeding
        self.reseeding = reseeding
        self.num_groups = num_groups
        self.rr_num_advance = rr_num_advance

        self.round_results = list[list[TournamentRound]]()

        self.stats = None
        self.attached = False
        self.started = False

        self.listeners = []
        self.id = tournament_id

        self.seed_players()

    def begin(self) -> bool:
        if self.type == TournamentElimination.DOUBLE:
            return False
        if not self.started:
            self.round_results.append(list[TournamentRound]())
            for group in self.groups:
                match self.type:
                    case TournamentElimination.SINGLE:
                        tournament_round = KnockoutRound(0,group,True)
                    case TournamentElimination.ROUND_ROBIN | TournamentElimination.WORLD_CUP:
                        tournament_round = RoundRobinRound(0,group,True,num_advance=self.rr_num_advance)
                    case _:
                        logger.warning("Unknown elimination type %s", self.type)
                        tournament_round = RoundRobinRound(0,group,True,num_advance=self.rr_num_advance)
                self.started = True
                tournament_round.add_listener(self)
                self.round_results[0].append(tournament_round)
            return True
        return False

    def advance(self) -> bool:
        if self.started:
            if self.round_over() and not self.is_over():
                round_number = len(self.round_results)
                if self.type == TournamentElimination.SINGLE:
                    merge_groups = False
                    for group in self.round_results[-1]:
                        if len(group.advancers()) <= 1:
                            merge_groups = True
                    self.round_results.append(list[TournamentRound]())
                    if merge_groups:
                        players = list[str]()
                    for group in self.round_results[-2]:
                        if merge_groups:
                            players.append(group.advancers())
                        else:
                            tournament_round = KnockoutRound(round_number,self.players,self.reseeding,group.advancers())
                            tournament_round.add_listener(self)
                            self.round_results[-1].append(tournament_round)
                    if merge_groups:
                        tournament_round = KnockoutRound(round_number,self.players,self.reseeding,players)
                        tournament_round.add_listener(self)
                        self.round_results[-1].append(tournament_round)
                elif self.type == TournamentElimination.WORLD_CUP:
                    players = list[str]()
                    for group in self.round_results[-2]:
                        players.append(group.advancers())
                    tournament_round = KnockoutRound(round_number,self.players,self.reseeding,players)
                    tournament_round.add_listener(self)
                    self.round_results.append(tournament_round)
                elif self.type == TournamentElimination.ROUND_ROBIN:
                    merge_groups = False
                    for group in self.round_results[-1]:
                        if len(group.advancers()) <= self.rr_num_advance:
                            merge_groups = True
                    self.round_results.append(list[TournamentRound]())
                    if merge_groups:
                        players = list[str]()
                    for group in self.round_results[-2]:
                        if merge_groups:
                            players.append(group.advancers())
                        else:
                            tournament_round = RoundRobinRound(round_number,self.players,self.reseeding,group.advancers(),self.rr_num_advance)
                            tournament_round.add_listener(self)
                            self.round_results[-1].append(tournament_round)
                    if merge_groups:
                        tournament_round = KnockoutRound(round_number,self.players,self.reseeding,players)
                        tournament_round.add_listener(self)
                        self.round_results[-1].append(tournament_round)
                return True
        return False

    def update_round(self, _round_id):
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
            return self.round_results[-1][0].advancers()[0]

    def is_over(self):
        if not self.started:
            return False
        for group in self.round_results[-1]:
            if not group.is_over():
                return False
            if len(group.advancers()) > 1:
                return False
        return True

    def round_over(self) -> bool:
        for group in self.round_results[-1]:
            if not group.is_over():
                return False
        return True

    def sim_round(self) -> bool:
        pass

    def add_game(self, game:foosballgame.FoosballGame) -> None:
        pass

    def seed_players(self) -> None:
        if not self.started:
            if self.seeding == TournamentSeeding.RANDOM:
                random.shuffle(self.players)
            elif self.seeding == TournamentSeeding.SKILL:
                if self.attached:
                    self.players.sort(key=self.stats.skill_tracker.get_rating, reverse=True)
            self.group_players()

    def group_players(self) -> None:
        if not self.started:
            self.groups.clear()
            for _ in range(self.num_groups):
                self.groups.append([])
            i = 0
            for player in self.players:
                if (i // self.num_groups) % 2 == 0:
                    self.groups[i%self.num_groups].append(player)
                else:
                    self.groups[self.num_groups-1-(i%self.num_groups)].append(player)
                i += 1

    def list_games(self, round_number:int=None) -> list[foosballgame.FoosballMatchup]:
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
            self.seeding = TournamentSeeding.AS_ENTERED

    def set_seed(self, player:str, seed:int):
        if not self.started:
            if player in self.players:
                self.players.remove(player)
            self.players.insert(seed,player)
            self.seeding = TournamentSeeding.AS_ENTERED

    def get_win_odds(self, player:str) -> float:
        pass

    def get_performance(self, player:str) -> any:
        pass

    def attach(self, stats: statcollector.StatCollector) -> None:
        if not self.attached:
            self.stats = stats
            self.attached = True
            if self.seeding == TournamentSeeding.SKILL:
                self.seed_players()

    def detach(self) -> None:
        self.stats = None
        self.attached = False

class TournamentRound:

    def __init__(self, round_id, seeded_players:list[str], reseeding:bool, prev_winners:list[str]=None):
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
        self.reseeding = reseeding

        self.matchups = list[foosballgame.FoosballMatchup]()
        self.attached = False
        self.stats = None
        self.listeners = []
        self.id = round_id
        self.set_matchups()

    def add_listener(self, listener):
        self.listeners.append(listener)

    def notify_listeners(self):
        for listener in self.listeners:
            listener.update_round(self.id)

    def set_matchups(self):
        raise NotImplementedError()

    def update_matchup(self, _matchup):
        if self.is_over():
            self.notify_listeners()

    def is_over(self) -> bool:
        for matchup in self.matchups:
            if not matchup.is_over():
                return False
        return True

    def advancers(self) -> list[str]:
        raise NotImplementedError()

    def eliminated(self) -> list[str]:
        raise NotImplementedError()

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

    def attach(self, stats: statcollector.StatCollector) -> bool:
        if not self.attached:
            self.attached = True
            self.stats = stats
            return True
        return False

    def detach(self) -> None:
        self.stats = None
        self.attached = False

class KnockoutRound(TournamentRound):

    def set_matchups(self):
        num_players = len(self.round_players)
        pow_2 = 1
        while (pow_2 << 1) < num_players:
            pow_2 = pow_2 << 1
        num_to_eliminate = num_players - pow_2
        num_round = 2*num_to_eliminate
        if self.reseeding:
            self.round_players.sort(key=self.seeded_players.index)
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

    def advancers(self) -> list[str]:
        advancers = list[str]()
        advancers.extend(self.bye_players)
        for matchup in self.matchups:
            if matchup.is_over():
                advancers.append(matchup.winner())
        return advancers

    def eliminated(self) -> list[str]:
        eliminated = list[str]()
        for matchup in self.matchups:
            if matchup.is_over():
                eliminated.append(matchup.loser())
        return eliminated


class RoundRobinRound(TournamentRound):

    def __init__(self, round_id, seeded_players:list[str], reseeding:bool, prev_winners:list[str]=None, num_advance:int=1):
        self.num_advance = num_advance
        self.standings = statcollector.StatCollector([])
        super().__init__(round_id,seeded_players,reseeding,prev_winners)

    def set_matchups(self):
        for i in range(len(self.round_players)-1):
            for j in range(i+1,len(self.round_players)):
                matchup = foosballgame.FoosballMatchup(self.round_players[i],self.round_players[j],i)
                matchup.add_listener(self)
                self.matchups.append(matchup)
        random.shuffle(self.matchups)

    def advancers(self) -> list[str]:
        if self.is_over():
            return self.get_rank()[:self.num_advance]

    def eliminated(self) -> list[str]:
        if self.is_over():
            return self.get_rank()[self.num_advance:]

    def get_rank(self):
        rank = list(self.round_players)
        #rank.sort(key = lambda x: self.order_tup(x), reverse=True)
        return rank

    def order_tup(self, player):
        stats = self.standings.get_stats('standings')['Name'==player]
        return (stats['W'], stats['GF']-stats['GA'])

    def get_rank_dep(self, _players:list[str], _stats:statcollector.StatCollector, _start:str='W1') -> list[str]:
        ranking = list[str]()
        buckets = list[list[str]]()
        max_wins = self.standings.get_stats('standings')['W'].max()
        for _ in range(max_wins):
            buckets.append(list[str]())
        for player in self.round_players:
            buckets[self.standings.get_stat('W','individual')['Name'==player]['W']] = player
        for i in range(max_wins-1,-1,-1):
            if len(buckets[i]) == 1:
                ranking.append(buckets[i][0])
            elif len(buckets[i]) == 2:
                matches = self.standings.get_stats('matchups')
                if matches['Name'==buckets[i][0]]['W'] >= matches['Name'==buckets[i][0]['L']]:
                    ranking.append(buckets[i][0])
                    ranking.append(buckets[i][1])
                else:
                    ranking.append(buckets[i][1])
                    ranking.append(buckets[i][0])
            elif len(buckets[i]) >= 3:
                game_filter = gamefilter.GameFilter()
                game_filter.winners = list(buckets[i])
                game_filter.losers = list(buckets[i])
                order = self.get_rank()
                ranking.extend(order)
        return ranking

    def tie_breaker(self, player):
        pass

    def update_matchup(self, matchup:foosballgame.FoosballMatchup):
        super().update_matchup(matchup)
        if matchup.is_over():
            self.standings.add_game(matchup)
