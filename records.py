import statcollector as sc

"""
Records to keep:
- wins
- goals
- games
- win streak

Timeframes:
- all time
- filtered
- semester
- day
"""

class Records():

    def __init__(self):
        self.stats = None
        self.attached = False

        self.categories = dict[str,str]({'wins':'W', 'goals':'GF', 'games':'G', 'win streak':'LWS'})
        self.time_frames = list[str](['all time', 'filtered', 'semester', 'day'])

    def get_categories(self):
        return list(self.categories.keys())
    
    def get_time_frames(self):
        return self.time_frames

    def get_record(self, category:str, time_frame:str) -> tuple[int, list[str]]:
        if category in self.categories and time_frame in self.time_frames:
            if time_frame == 'all time':
                pass
            elif time_frame == 'filtered':
                stats = self.stats.get_stat(self.categories[category],'individual')
                max = stats[stats[self.categories[category]]==stats[self.categories[category]].max()]
                return (max[self.categories[category]].iloc[0], list(max['Name']))
            elif time_frame == 'semester':
                pass
            elif time_frame == 'day':
                pass
        return (0,[])

    def attach(self, stats:sc.StatCollector):
        if not self.attached:
            self.attached = True
            self.stats = stats

    def detach(self):
        self.attached = False
        self.stats = None