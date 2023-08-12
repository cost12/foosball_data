import statcollector as sc
import foosballgame

class Tournament:
    """
    Tournament Styles to consider:
    - random seed
    - ranked seed

    - single elimination
    - double elimination
    - round robin

    - round reseeding
    - fixed bracket
    """

    def __init__(self, players:list[str]=None,random_seeding:bool=False, reseeding:bool=False):
        if players is None:
            self.players = list[str]()
        else:
            self.players = players

        self.started = False
        self.seeds = dict[str,int]()
        self.random_seeding = random_seeding
        self.reseeding = reseeding

        self.round_results = list[list[foosballgame.FoosballGame]]()

        self.stats = None
        self.attached = False

    def sim_round(self) -> None:
        pass

    def add_game(self) -> None:
        pass

    def seed_players(self) -> None:
        pass

    def list_games(self, round:int=None) -> list[foosballgame.FoosballGame]:
        pass

    def add_player(self, player:str) -> None:
        pass

    def add_players(self, players:list[str]) -> None:
        pass

    def remove_player(self, player:str) -> bool:
        pass

    def remove_players(self, players:list[str]) -> bool:
        pass

    def set_players(self, players:list[str]) -> None:
        pass

    def set_seeding(self, seeding:dict[str,int]) -> bool:
        pass

    def set_seed(self, player:str, seed:int) -> bool:
        pass

    def get_win_odds(self, player:str) -> float:
        pass

    def get_performance(self, player:str) -> any:
        pass

    def attach(self, stats:sc.StatCollector) -> None:
        if not self.attached:
            self.stats = stats
            self.attached = True

    def detach(self) -> None:
        self.stats = None
        self.attached = False