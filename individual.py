import statcollector as sc
import foosballgame

class IndividualStats():

    def __init__(self, name:str, stats:sc.StatCollector):
        self.name = name
        self.stats = stats

    def get_record(self, filtered:bool=False) -> tuple[int,int]:
        if filtered:
            return self.stats.get_stat('W','individual')[self.name], self.stats.get_stat('L','individual')[self.name]
        else:
            return foosballgame.get_record(self.stats.games,self.name)

    def get_goals(self, filtered:bool=False):
        if filtered:
            return self.stats.get_stat('GF','individual')[self.name], self.stats.get_stat('GA','individual')[self.name]
        else:
            return foosballgame.get_goals_scored(self.stats.games,self.name)

    def rank_opponents(self):
        pass

    def get_closest_opponent(self):
        pass

