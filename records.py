import statcollector as sc
import event_date

import datetime
import pandas as pd

class TimeFrame:

    def __init__(self, name:str, type:str):
        self.name = name
        self.type = type

    def selector(self) -> bool:
        if self.is_day():
            return 'Date'
        elif self.is_semester():
            return 'Semester'
        else:
            return None

    def is_day(self) -> bool:
        return self.type.lower() == 'day'

    def is_semester(self) -> bool:
        return self.type.lower() == 'semester'

    def is_all(self) -> bool:
        return self.type.lower() == 'all'
    
    def get_string(self) -> str:
        if self.is_day() and not self.name == 'day':
            return self.name + ' day'
        else:
            return self.name

class Performance:

    def __init__(self, category:str, time_frame:TimeFrame, player_name:str, result:float,*, semester:str=None, on_date:datetime.date=None, to_date:datetime.date=None):
        self.category = category
        self.time_frame = time_frame
        self.player = player_name
        self.result = result
        self.on_date = on_date
        self.to_date = to_date
        self.semester = semester

    def is_across_dates(self):
        return self.to_date is not None and not self.on_date == self.to_date
    
    def has_date(self):
        return self.on_date is not None
    
    def has_semester(self):
        return self.semester is not None

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

class Records:

    def __init__(self):
        self.stats = None
        self.semesters = dict[str,event_date.EventDate]()
        self.attached = False

        self.categories = dict[str,str]({'wins':'W', 'goals':'GF', 'games':'G', 'win streak':'LWS'})
        self.time_frames = list[TimeFrame]([TimeFrame('all','all'), TimeFrame('semester','semester'), TimeFrame('day','day')])

    def get_categories(self):
        return list(self.categories.keys())
    
    def get_time_frames(self):
        return self.time_frames

    def get_top_performances(self, category:str, time_frame:TimeFrame, n:int=1) -> Performance:
        if category in self.categories and time_frame in self.time_frames:
            if time_frame.is_all():
                if category == 'win streak':
                    stats = self.stats.get_stats('games')
                    return self.__get_top_win_streaks(stats, time_frame, n)
                stats = self.stats.get_stat(self.categories[category],'individual')
                best = stats.nlargest(n,self.categories[category],'all')
                performances = []
                for i in range(len(best.index)):
                    performances.append(Performance(category,time_frame,best.iloc[i]['Name'],best.iloc[i][self.categories[category]]))
                return performances
            elif time_frame.name == 'semester':
                stats = self.stats.get_stats('games')
                stats['Semester'] = stats['Date'].apply(lambda date: event_date.get_event(date,list(self.semesters.values())).name)
            elif time_frame.name == 'day':
                stats = self.stats.get_stats('games')
            elif time_frame.is_day():
                stats = self.stats.get_stats('games')
                semester = time_frame.name
                stats['Filter'] = stats['Date'].apply(lambda date: self.semesters[semester].contains_date(date))
                stats = stats[stats['Filter']==True]
            elif time_frame.is_semester():
                stats = self.stats.get_stats('games')
                semester = time_frame.name
                stats['Semester'] = stats['Date'].apply(lambda date: event_date.get_event(date,list(self.semesters.values())).name)
                stats['Filter'] = stats['Date'].apply(lambda date: self.semesters[semester].contains_date(date))
                stats = stats[stats['Filter']==True]

            if not time_frame.is_all():
                if category == 'wins':
                    best = stats.groupby(['Winner', time_frame.selector()]).size().reset_index(name=self.categories[category])
                    best = best.nlargest(n,self.categories[category],'all')
                    performances = []
                    for i in range(len(best.index)):
                        if time_frame.is_day():
                            performances.append(Performance(category,time_frame,best.iloc[i]['Winner'],best.iloc[i][self.categories[category]],on_date=best.iloc[i][time_frame.selector()]))
                        else: # Semester
                            #best['First'] = 
                            performances.append(Performance(category,time_frame,best.iloc[i]['Winner'],best.iloc[i][self.categories[category]],semester=best.iloc[i][time_frame.selector()]))
                    return performances
                elif category == 'goals':
                    w_goals = stats.groupby(['Winner', time_frame.selector()])['Winner Score'].sum().reset_index()
                    l_goals = stats.groupby(['Loser',  time_frame.selector()])['Loser Score'].sum().reset_index()
                    w_goals = w_goals.rename(columns={'Winner':'Name'})
                    l_goals = l_goals.rename(columns={'Loser':'Name'})
                    goals = w_goals.join(l_goals.set_index(['Name',time_frame.selector()]), ['Name',time_frame.selector()], 'outer')
                    goals = goals.fillna(0)
                    goals = goals.astype({'Loser Score':int,'Winner Score':int})
                    goals[self.categories[category]] = goals['Winner Score']+goals['Loser Score']
                    best = goals.nlargest(n,self.categories[category],'all')
                    performances = []
                    for i in range(len(best.index)):
                        if time_frame.is_day():
                            performances.append(Performance(category,time_frame,best.iloc[i]['Name'],best.iloc[i][self.categories[category]],on_date=best.iloc[i][time_frame.selector()]))
                        else: # Semester
                            performances.append(Performance(category,time_frame,best.iloc[i]['Name'],best.iloc[i][self.categories[category]],semester=best.iloc[i][time_frame.selector()]))
                    return performances
                elif category == 'games':
                    wins =   stats.groupby(['Winner', time_frame.selector()]).size().reset_index(name='wins')
                    losses = stats.groupby(['Loser', time_frame.selector()]).size().reset_index(name='losses')
                    wins =   wins.rename(columns={'Winner':'Name'})
                    losses = losses.rename(columns={'Loser':'Name'})
                    games = wins.join(losses.set_index(['Name',time_frame.selector()]), ['Name',time_frame.selector()], 'outer')
                    games = games.fillna(0)
                    games = games.astype({'losses':int, 'wins':int})
                    games[self.categories[category]] = games['wins']+games['losses']
                    best = games.nlargest(n,self.categories[category],'all')
                    performances = []
                    for i in range(len(best.index)):
                        if time_frame.is_day():
                            performances.append(Performance(category,time_frame,best.iloc[i]['Name'],best.iloc[i][self.categories[category]],on_date=best.iloc[i][time_frame.selector()]))
                        else: # Semester
                            performances.append(Performance(category,time_frame,best.iloc[i]['Name'],best.iloc[i][self.categories[category]],semester=best.iloc[i][time_frame.selector()]))
                    return performances
                elif category == 'win streak':
                    return self.__get_top_win_streaks(stats, time_frame, n)
        return []
    

    def __get_top_win_streaks(self, stats:pd.DataFrame, time_frame:TimeFrame, n:int):
        cutoff = 0
        performances = list[Performance]()
        counts = dict[str,Performance]()
        cur_time = None
        for i in range(0,len(stats.index)):
            winner = stats['Winner'].iloc[i]
            loser =  stats['Loser'].iloc[i]
            if time_frame.is_all():
                time = 1 # constant, same for all
            else:
                time =   stats[time_frame.selector()].iloc[i]
            date =   stats['Date'].iloc[i]

            if loser in counts:
                if counts[loser].result == cutoff:
                    performances.append(counts[loser])
                elif counts[loser].result > cutoff:
                    places = 0
                    tied = 0
                    i = 0
                    performances.sort(key=lambda x: x.result, reverse=True)
                    for performance in performances:
                        if performance.result < cutoff:
                            performances.remove(performance)
                        if i > 0 and performance.result < performances[i-1].result:
                            places += tied + 1
                            tied = 0
                            if places > n:
                                cutoff = performances[i-1].result
                        elif i > 0 and performance.result == performances[i-1].result:
                            tied += 1
                        i+=1
                    performances.append(counts[loser])
                del counts[loser]

            if cur_time == time:
                if winner in counts:
                    counts[winner].result += 1
                    counts[winner].to_date = date
                else:
                    counts[winner] = Performance('win streak',time_frame,winner,1,on_date=date,to_date=date)
            elif cur_time is None:
                cur_time = time
                counts[winner] = Performance('win streak',time_frame,winner,1,on_date=date,to_date=date)
            else:
                cutoff = self.__update_performances(performances,counts,n,cutoff)
                cur_time = time
                counts[winner] = Performance('win streak',time_frame,winner,1,on_date=date,to_date=date)
        self.__update_performances(performances,counts,n,cutoff)
        return performances
    
    def __update_performances(self, performances:list[Performance], counts:dict[str,Performance], n:int, cutoff:int) -> int:
        for name in counts.keys():
            if counts[name].result == cutoff:
                performances.append(counts[name])
            elif counts[name].result > cutoff:
                places = 0
                tied = 0
                i = 0
                performances.sort(key=lambda x: x.result, reverse=True)
                for performance in performances:
                    if performance.result < cutoff:
                        performances.remove(performance)
                    if i > 0 and performance.result < performances[i-1].result:
                        places += tied + 1
                        tied = 0
                        if places > n:
                            cutoff = performances[i-1].result
                    elif i > 0 and performance.result == performances[i-1].result:
                        tied += 1
                    i+=1
                performances.append(counts[name])
        counts.clear()
        return cutoff

    def attach(self, stats:sc.StatCollector, semesters:list[event_date.EventDate]):
        if not self.attached:
            self.attached = True
            self.stats = stats

            for semester in semesters:
                self.semesters[semester.name] = semester
                self.time_frames.append(TimeFrame(semester.name,'semester'))
                self.time_frames.append(TimeFrame(semester.name,'day'))

    def detach(self):
        self.attached = False
        self.stats = None
        self.semesters.clear()

        self.time_frames = list[TimeFrame]([TimeFrame('all','all'), TimeFrame('semester','semester'), TimeFrame('day','day')])