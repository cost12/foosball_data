import statcollector as sc

class IndividualStats():

    def __init__(self, name:str, stats:sc.StatCollector):
        self.name = name
        self.stats = stats

    def get_record(self, filtered:bool=False):
        pass

    def get_goals(self, filtered:bool=False):
        pass

    def rank_opponents(self):
        pass

    def get_closest_opponent(self):
        pass

