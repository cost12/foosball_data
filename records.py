import statcollector as sc
import event_date

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
        self.semesters = None
        self.attached = False

        self.categories = dict[str,str]({'wins':'W', 'goals':'GF', 'games':'G', 'win streak':'LWS'})
        self.time_frames = list[str](['all time', 'filtered', 'semester', 'filtered semester', 'day', 'filtered day'])

    def get_categories(self):
        return list(self.categories.keys())
    
    def get_time_frames(self):
        return self.time_frames

    def get_record(self, category:str, time_frame:str) -> tuple[int, list]:
        if category in self.categories and time_frame in self.time_frames:
            if time_frame == 'all time':
                pass
            elif time_frame == 'filtered':
                stats = self.stats.get_stat(self.categories[category],'individual')
                max = stats[stats[self.categories[category]]==stats[self.categories[category]].max()]
                return (max[self.categories[category]].iloc[0], list(max['Name']))
            elif time_frame == 'semester':
                pass
            elif time_frame == 'filtered semester':
                stats = self.stats.get_stats('games')
                stats['Semester'] = stats['Date'].apply(lambda date: event_date.get_event(date,self.semesters).name)
                secondary = 'Semester'
            elif time_frame == 'day':
                pass
            elif time_frame == 'filtered day':
                stats = self.stats.get_stats('games')
                secondary = 'Date'

            if time_frame in ['filtered semester', 'filtered day']:
                if category == 'wins':
                    max = stats.groupby(['Winner', secondary]).size().reset_index(name='count')
                    max = max[max['count']==max['count'].max()]
                    return (max['count'].iloc[0],list(max[['Winner',secondary]].itertuples(index=False, name=None)))
                elif category == 'goals':
                    w_goals = stats.groupby(['Winner', secondary])['Winner Score'].sum().reset_index()
                    l_goals = stats.groupby(['Loser',  secondary])['Loser Score'].sum().reset_index()
                    w_goals = w_goals.rename(columns={'Winner':'Name'})
                    l_goals = l_goals.rename(columns={'Loser':'Name'})
                    goals = w_goals.join(l_goals.set_index(['Name',secondary]), ['Name',secondary])
                    goals = goals.fillna(0)
                    goals = goals.astype({'Loser Score':int})
                    goals['goals'] = goals['Winner Score']+goals['Loser Score']
                    max = goals[goals['goals']==goals['goals'].max()]
                    return (max['goals'].iloc[0],list(max[['Name',secondary]].itertuples(index=False, name=None)))
                elif category == 'games':
                    wins =   stats.groupby(['Winner', secondary]).size().reset_index(name='wins')
                    losses = stats.groupby(['Loser', secondary]).size().reset_index(name='losses')
                    wins =   wins.rename(columns={'Winner':'Name'})
                    losses = losses.rename(columns={'Loser':'Name'})
                    games = wins.join(losses.set_index(['Name',secondary]), ['Name',secondary])
                    games = games.fillna(0)
                    games = games.astype({'losses':int})
                    games['games'] = games['wins']+games['losses']
                    max = games[games['games']==games['games'].max()]
                    return (max['games'].iloc[0],list(max[['Name',secondary]].itertuples(index=False, name=None)))
                elif category == 'win streak':
                    best_streak = 0
                    names = []
                    counts = dict[str,int]()
                    cur_date = None
                    for i in range(0,len(stats.index)):
                        winner = stats['Winner'].iloc[i]
                        loser =  stats['Loser'].iloc[i]
                        date =   stats[secondary].iloc[i]
                        if loser in counts:
                            if counts[loser] == best_streak:
                                names.append((loser,cur_date))
                            elif counts[loser] > best_streak:
                                names.clear()
                                names.append((loser,cur_date))
                                best_streak = counts[loser]
                            counts[loser] = 0
                        if cur_date == date:
                            if winner in counts:
                                counts[winner] += 1
                            else:
                                counts[winner] = 1
                        elif cur_date is None:
                            cur_date = date
                            counts[winner] = 1
                        else:
                            for name in counts.keys():
                                if counts[name] == best_streak:
                                    names.append((name,cur_date))
                                elif counts[name] > best_streak:
                                    best_streak = counts[name]
                                    names.clear()
                                    names.append((name, cur_date))
                            cur_date = date
                            counts.clear()
                    return (best_streak,names)

        return (0,[])

    def attach(self, stats:sc.StatCollector, semesters:list[event_date.EventDate]):
        if not self.attached:
            self.attached = True
            self.stats = stats
            self.semesters = semesters

    def detach(self):
        self.attached = False
        self.stats = None
        self.semesters = None