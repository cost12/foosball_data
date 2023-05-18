import tkinter as tk
from tkinter import ttk
from typing import Union
import pandas as pd
import matplotlib.pyplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import statcollector as sc
import event_date
import gamefilter
import graphsyousee
import foosballgame
import colley
import elo

"""
TODO:
classes needed:
    Filter
    FilterView
    Graph
    GraphView
    IndividualView
    LegendsView
"""

"""
Main loop for tkinter
"""
def visualize_foosball(games,dates) -> None:
    root = tk.Tk()
    root.rowconfigure(0,weight=1)
    root.columnconfigure(0,weight=1)

    stats = sc.StatCollector(games)
    viewControl = StatsViewControl(root,stats,dates)

    root.mainloop()

"""
Decides which frames are displayed

Displays to add
 - graphs
 - individual
 - news/legends
"""
class StatsViewControl(ttk.Frame):

    def __init__(self,frm:ttk.Frame,stats:sc.StatCollector,dates:list[event_date.EventDate]) -> None:
        super().__init__(frm)
        self.frm=frm

        self.stats = stats
        self.dates = dates
        self.filter = gamefilter.GameFilter()
        self.view = str('table')
        self.views = {'table':      StatTable(frm,self.stats),
                      'sim':        SimView(frm,self.stats),
                      'graphs':     GraphView(frm,self.stats), #TODO: implement these/ come up with more
                      #'individual': [],
                      #'legends':    [],
                      #'records':    [],
                      'filter':     FilterView(frm,self.stats,self.filter,self.dates)}

        self.add_buttons()

        for view in self.views:
            self.views[view].pack()
        for view in self.views:
            if not view == 'table':
                self.views[view].forget()

    """
    Add buttons for each view/frame and each semester/timeframe
    """
    def add_buttons(self) -> None:
        # view buttons
        view_frm = ttk.Frame(self.frm)
        view_frm.pack()
        c=0
        for view in self.views.keys():
            def change_v(v=view):
                self.change_view(v)
            ttk.Button(view_frm,text=view,command=change_v).grid(row=0,column=c)
            view_frm.columnconfigure(c,weight=1)
            c+=1

        if 0:
            # semester buttons
            filter_frm = ttk.Frame(self.frm)
            filter_frm.pack()
            filter_frm.columnconfigure(0,weight=1)
            def reset_filt():
                self.stats.reset_filter()
                for view in self.views:
                    self.views[view].filter_reset()
                self.views[self.view].pack()
            ttk.Button(filter_frm, text='All Time',command=reset_filt).grid(row=0,column=0)
            c=1
            for semester in self.dates:
                def filter(date=semester):
                    self.stats.filter_by_date(date)
                    for view in self.views:
                        self.views[view].filter_applied(date.name)
                    self.views[self.view].pack()
                ttk.Button(filter_frm, text=semester.name,command=filter).grid(row=0,column=c)
                filter_frm.columnconfigure(c,weight=1)
                c+=1

    """
    Reload the current frame

    def reload(self) -> None:
        self.views[self.view].reload()
    """

    """
    Change from one frame to another
    """
    def change_view(self,view:str) -> None:
        if view in self.views and view != self.view:
            self.views[self.view].forget()
            self.view = view
            self.views[self.view].reset()
            self.views[self.view].pack()

    """
    Repack the current frame
    
    def repack(self) -> None:
        self.views[self.view].pack()
    """

"""
Interaction and visulization for Simulator
"""
class SimView(ttk.Frame):

    def __init__(self,frm:ttk.Frame,stats:sc.StatCollector,p1:str='',p2:str='') -> None:
        super().__init__(frm)
        self.frm = frm
        
        self.stats = stats

        self.time_str = 'All Time'
        self.show_probs = True

        self.player1=tk.StringVar()
        self.player2=tk.StringVar()
        self.simulator = self.stats.get_simulator(self.player1.get(),self.player2.get())

        self.columnconfigure(0,weight=5)
        self.columnconfigure(1,weight=1)
        self.columnconfigure(2,weight=5)
        self.rowconfigure(0,weight=2)
        self.rowconfigure(1,weight=1)
        self.rowconfigure(2,weight=2)
        self.rowconfigure(3,weight=1)
        self.rowconfigure(4,weight=1)
        self.rowconfigure(5,weight=1)
        self.rowconfigure(6,weight=1)
        self.rowconfigure(7,weight=1)
        self.rowconfigure(8,weight=1)
        self.rowconfigure(9,weight=1)

        r = 0
        # top row
        self.p1_ent = ttk.Entry(self,textvariable=self.player1)
        self.p1_ent.grid(row=r, column=0,sticky='news')
        self.p1_ent.insert(0,p1)
        self.reset_btn = ttk.Button(self, text='Reset', command=self.reset)
        self.reset_btn.grid(row=r, column=1,sticky='news')
        self.p2_ent = ttk.Entry(self,textvariable=self.player2)
        self.p2_ent.grid(row=r, column=2,sticky='news')
        self.p2_ent.insert(0,p2)

        r += 1
        # row 1
        self.score_lbl1 = ttk.Label(self, text='score:',anchor='e')
        self.score_lbl1.grid(row=r,column=0,sticky='news')
        self.sim_goal_btn = ttk.Button(self, text='Sim goal', command=self.sim_goal)
        self.sim_goal_btn.grid(row=r, column=1,sticky='news')
        self.score_lbl2 = ttk.Label(self, text='score:')
        self.score_lbl2.grid(row=r,column=2,sticky='news')

        r += 1
        # row 2
        self.score_num1 = ttk.Label(self, text=self.simulator.sim_score1,anchor='e')
        self.score_num1.grid(row=r,column=0,sticky='news')
        self.sim_game_btn = ttk.Button(self, text='Sim Game', command=self.sim_game)
        self.sim_game_btn.grid(row=r, column=1,sticky='news')
        self.score_num2 = ttk.Label(self, text=self.simulator.sim_score2)
        self.score_num2.grid(row=r,column=2,sticky='news')

        r += 1
        # row 3
        self.win_prob_lbl1 =  ttk.Label(self, text='win prob',anchor='e')
        self.win_prob_lbl1.grid(row=r,column=0,sticky='news')
        self.time_frame_lbl = ttk.Label(self, text=self.time_str,anchor='c')
        self.time_frame_lbl.grid(row=r,column=1,sticky='news')
        self.win_prob_lbl2 =  ttk.Label(self, text='win prob',anchor='w')
        self.win_prob_lbl2.grid(row=r,column=2,sticky='news')

        r += 1
        # row 4
        text = '{:>.3f}%'.format(self.simulator.get_p1_win_odds()*100)
        self.win_prob_num1 = ttk.Label(self, text=text,anchor='e')
        self.win_prob_num1.grid(row=r,column=0,sticky='news')
        text = '{:>.3f}%'.format((1-self.simulator.get_p1_win_odds())*100)
        self.win_prob_num2 = ttk.Label(self, text=text)
        self.win_prob_num2.grid(row=r,column=2,sticky='news')

        r += 1
        # row 5
        self.exp_score_lbl1 = ttk.Label(self, text='exp score',anchor='e')
        self.exp_score_lbl1.grid(row=r,column=0,sticky='news')
        self.exp_score_lbl2 = ttk.Label(self, text='exp score',anchor='w')
        self.exp_score_lbl2.grid(row=r,column=2,sticky='news')

        r += 1
        # row 6
        text = '{:>.3f}'.format(self.simulator.get_expected_score(self.simulator.player1))
        self.exp_score_num1 = ttk.Label(self, text=text,anchor='e')
        self.exp_score_num1.grid(row=r,column=0,sticky='news')
        text = '{:>.3f}'.format(self.simulator.get_expected_score(self.simulator.player2))
        self.exp_score_num2 = ttk.Label(self, text=text)
        self.exp_score_num2.grid(row=r,column=2,sticky='news')

        r += 1
        # row 7
        self.prob_score_lbl1 = ttk.Label(self, text='prob score',anchor='e')
        self.prob_score_lbl1.grid(row=r,column=0,sticky='news')
        self.prob_score_lbl2 = ttk.Label(self, text='prob score',anchor='w')
        self.prob_score_lbl2.grid(row=r,column=2,sticky='news')

        r += 1
        # row 8
        self.prob_score_num1 = ttk.Label(self, text=self.simulator.get_most_probable_score(self.simulator.player1),anchor='e')
        self.prob_score_num1.grid(row=r,column=0,sticky='news')
        self.prob_score_num2 = ttk.Label(self, text=self.simulator.get_most_probable_score(self.simulator.player2),anchor='w')
        self.prob_score_num2.grid(row=r,column=2,sticky='news')

        r += 1
        # row 9
        self.add_goal_btn1 = ttk.Button(self, text='Add Goal', command=lambda : self.add_goal(self.simulator.player1))
        self.add_goal_btn1.grid(row=r,column=0,sticky='news')
        self.add_goal_btn2 = ttk.Button(self, text='Add Goal', command=lambda : self.add_goal(self.simulator.player2))
        self.add_goal_btn2.grid(row=r,column=2,sticky='news')

        r += 1
        # row 10 (wins)
        self.wins_lbl1 = ttk.Label(self, text=0, anchor='e')
        self.wins_lbl1.grid(row=r,column=0,sticky='news')
        ttk.Label(self, text='wins', anchor='c').grid(row=r,column=1,sticky='news')
        self.wins_lbl2 = ttk.Label(self, text=0, anchor='w')
        self.wins_lbl2.grid(row=r,column=2,sticky='news')

        r += 1
        # row 11 (goals)
        self.goals_lbl1 = ttk.Label(self, text=0, anchor='e')
        self.goals_lbl1.grid(row=r,column=0,sticky='news')
        ttk.Label(self, text='goals', anchor='c').grid(row=r,column=1,sticky='news')
        self.goals_lbl2 = ttk.Label(self, text=0, anchor='w')
        self.goals_lbl2.grid(row=r,column=2,sticky='news')

        r+=1
        def toggle():
            self.show_probs = not self.show_probs
            self.update_labels()
        ttk.Button(self, text='Scores', command=toggle).grid(row=r,column=1,sticky='news')

        self.score_lbls_p1 = []
        self.score_lbls_p2 = []
        for i in range(0,11):
            r += 1
            p1_lbl = ttk.Label(self, text=0, anchor='e')
            p1_lbl.grid(row=r,column=0,sticky='news')
            ttk.Label(self,text=i,anchor='c').grid(row=r,column=1,sticky='news')
            p2_lbl = ttk.Label(self, text=0, anchor='w')
            p2_lbl.grid(row=r,column=2,sticky='news')

            self.score_lbls_p1.append(p1_lbl)
            self.score_lbls_p2.append(p2_lbl)

    
    """
    Redraws everything
    """
    def reload(self) -> None:
        self.destroy()
        self.__init__(self.frm,self.stats,self.player1.get(),self.player2.get())
        self.pack()

    """
    Resets the simulator
    """
    def reset(self) -> None:
        self.simulator.reset_simulator(self.player1.get(),self.player2.get())
        self.update_labels()

    """
    Simulate a goal
    """
    def sim_goal(self) -> None:
        self.simulator.simulate_goal()
        self.update_labels()

    """
    Simulate the game
    """
    def sim_game(self) -> None:
        self.simulator.simulate_game()
        self.update_labels()

    """
    Add a goal to a specified player's score
    """
    def add_goal(self,player:str) -> None:
        self.simulator.add_goal(player)
        self.update_labels()

    """
    Filter the games by a date range
    """
    def filter_applied(self,name:str) -> None:
        self.time_str = name
        self.reset()

    """
    Reset the filter/ go back to games from all time frames
    """
    def filter_reset(self) -> None:
        self.time_str = 'All Time'
        self.reset()

    """
    Updates the labels with new information from the simulation
    """
    def update_labels(self) -> None:
        self.time_frame_lbl.config(text=self.time_str)
        self.score_num1.config(text=self.simulator.sim_score1)
        self.score_num2.config(text=self.simulator.sim_score2)
        text = '{:>.3f}%'.format(self.simulator.get_p1_win_odds()*100)
        self.win_prob_num1.config(text=text)
        text = '{:>.3f}%'.format((1-self.simulator.get_p1_win_odds())*100)
        self.win_prob_num2.config(text=text)
        text = '{:>.3f}'.format(self.simulator.get_expected_score(self.simulator.player1))
        self.exp_score_num1.config(text=text)
        text = '{:>.3f}'.format(self.simulator.get_expected_score(self.simulator.player2))
        self.exp_score_num2.config(text=text)
        self.prob_score_num1.config(text=self.simulator.get_most_probable_score(self.simulator.player1))
        self.prob_score_num2.config(text=self.simulator.get_most_probable_score(self.simulator.player2))

        self.wins_lbl1.config(text=self.simulator.get_wins_for(self.simulator.player1))
        self.wins_lbl2.config(text=self.simulator.get_wins_for(self.simulator.player2))
        self.goals_lbl1.config(text=self.simulator.get_goals_for(self.simulator.player1))
        self.goals_lbl2.config(text=self.simulator.get_goals_for(self.simulator.player2))

        if self.show_probs:
            for i in range(0,11):
                text = '{:>.3f}'.format(self.simulator.get_prob_of_score(self.simulator.player1,i)*100)
                self.score_lbls_p1[i].config(text=text)
                text = '{:>.3f}'.format(self.simulator.get_prob_of_score(self.simulator.player2,i)*100)
                self.score_lbls_p2[i].config(text=text)
        else:
            for i in range(0,11):
                self.score_lbls_p1[i].config(text=self.simulator.get_times_scored_n(self.simulator.player1,i))
                self.score_lbls_p2[i].config(text=self.simulator.get_times_scored_n(self.simulator.player2,i))
            
"""
Interaction and visualization for StatCollector
"""
class StatTable(ttk.Frame):

    def __init__(self, frm:ttk.Frame, stats:sc.StatCollector, rmax:int=30, sort:list[str]=['W PCT'], asc:bool=False, view:str='players') -> None:
        super().__init__(frm)
        
        self.frm = frm
        self.stats = stats
        
        self.sort = sort
        self.ascending = asc
        self.view = view
        self.rmax = rmax
        
        self.highlight = 'white'
        self.background = 'gray'

        data = self.get_data()

        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        # headers
        for c in range(len(data.columns)):
            self.columnconfigure(c+1,weight=1) # for filling vertically
            header = data.columns[c]
            btn = ttk.Button(self, text=header,command=self.__sort_call(header))
            btn.grid(row=0, column=c+1,sticky='news')

        for r in range(min(data.shape[0],self.rmax)):
            self.rowconfigure(r+1,weight=1) # for filling horizontally
            # numbers
            lbl = ttk.Label(self, text=r+1, anchor='e')
            lbl.grid(row=r+1, column=0,sticky='news')

            # body
            for c in range(len(data.iloc[r])):
                background = self.background
                if len(self.sort) > 0 and self.sort[0] == data.columns[c]:
                    background = self.highlight
                text = data.iloc[r][c]
                anchor = 'e'
                if isinstance(text,str):
                    anchor = 'w'
                if isinstance(text,float):
                    text = '{:>.3f}'.format(text)
                lbl = ttk.Label(self, text=text, anchor=anchor,background=background)
                lbl.grid(row=r+1, column=c+1,sticky='news')

        c=0
        for stat in self.stats.list_stats():
            def set_v(v=stat):
                self.set_view(v)
            btn = ttk.Button(self, text=stat,command=set_v)
            btn.grid(row=r+2,column=c,sticky='news')
            c += 1

    """ TODO: instead of reloading every time, find a way to just change the labels
    Reload, currently used to update the view
    """
    def reload(self) -> None:
        self.destroy()
        self.__init__(self.frm,self.stats,self.rmax,self.sort,self.ascending,self.view)
        self.pack()

    def reset(self) -> None:
        self.reload()

    """
    Get data from the StatCollector and store it so it can be displayed
    """
    def get_data(self) -> pd.DataFrame:
        data = self.stats.get_stats(self.view)
        for s in self.sort:
            if s not in data.columns:
                self.sort.remove(s)
                print("removed " + s)
        if len(self.sort)>0:
            try:
                data = data.sort_values(by=self.sort, ascending=self.ascending)
            except:
                print(data.columns)
                print(self.sort)
                print("")
        return data

    """ TODO: find a better way than reloading to upadate the visualization
    Sets the main sort to be n and the direction is decided by ascending
    Calls reload so that the data is displayed as sorted
    """
    def sort_by(self, n:str, ascending:bool=None) -> None:
        if n in self.sort:
            self.sort.remove(n)
        self.sort.insert(0,n)
        if ascending is not None:
            self.ascending = ascending
        self.reload()

    """
    This is called when a button is clicked to sort the data
    Returns a lambda function that calls sort_by and passes in n and the correct direction
    """
    def __sort_call(self, n:str): # TODO: figure out how to type hint this
        ascending = self.ascending
        if len(self.sort) > 0 and self.sort[0] == n:
            ascending = not self.ascending
        return lambda:self.sort_by(n,ascending)

    """ TODO: find a better way than reloading
    Change the view to a different stat category
    """
    def set_view(self, view:str) -> None:
        if self.view != view:
            self.view = view
            self.reload()

    """ TODO: find a better way than reloading
    Filter the games by a date range
    """
    def filter_applied(self,name:str) -> None:
        self.reload()

    """ TODO: find a better way than reloading
    Reset the filter/ go back to games from all time frames
    """
    def filter_reset(self) -> None:
        self.reload()

"""
Interaction and visualization for a filter
"""
class FilterView(ttk.Frame):

    def __init__(self, frm:ttk.Frame, stats:sc.StatCollector, filter:gamefilter.GameFilter, events:list[event_date.EventDate]=[]) -> None:
        super().__init__(frm)

        self.frm = frm
        self.stats = stats
        self.filter = filter
        self.events = dict[str,event_date.EventDate]()
        for event in events:
            self.events[event.name] = event

        self.count_lbl = ttk.Label(self, text=f'({self.stats.count_filtered(self.filter)} games selected)')
        self.count_lbl.grid(row=0,column=0,columnspan=4)

        self.player_select = MultiSelector(self, 'Winner Select', stats.list_players())
        self.player_select.add_listener(self)
        self.player_select.grid(row=1,column=0,rowspan=4,sticky='news')

        self.player_select = MultiSelector(self, 'Loser Select', stats.list_players())
        self.player_select.add_listener(self)
        self.player_select.grid(row=1,column=1,rowspan=4,sticky='news')

        self.player_select = MultiSelector(self, 'Event Select', list(self.events.keys()))
        self.player_select.add_listener(self)
        self.player_select.grid(row=1,column=2,rowspan=2,sticky='news')

        self.loser_score_range = RangeAdjustor(self, 'Loser Score', 
                                               stats.min_score_loss(),     stats.max_score_loss(), 
                                               stats.min_score_possible(), stats.max_score_possible())
        self.loser_score_range.add_listener(self)
        self.loser_score_range.grid(row=1,column=3,sticky='news')

        self.number_range = RangeAdjustor(self, 'Number', 
                                          stats.min_num_selected(), stats.max_num_selected(), 
                                          stats.min_num(),          stats.max_num())
        self.number_range.add_listener(self)
        self.number_range.grid(row=2,column=3,sticky='news')

        ttk.Button(self,text='Apply',command=self.apply_filter).grid(row=4,column=2)
        #ttk.Button(self,text='Reset',command=self.reset_filter).grid(row=4,column=3)

    """
    Called by ViewControl
    """
    def reset(self) -> None:
        pass

    """
    Called by ViewControl
    """
    def reload(self) -> None:
        pass

    """
    Apply the chosen filter to the stats
    """
    def apply_filter(self) -> None:
        self.stats.apply_filter(self.filter)
        self.count_lbl.config(text=f'({self.stats.count_filtered(self.filter)} games selected)')

    """
    Reset the stats to the default filter
    """
    def reset_filter(self) -> None: #TODO: actually reset or just remove
        self.stats.reset_filter()
        self.count_lbl.config(text=f'({self.stats.count_filtered(self.filter)} games selected)')

    """
    Called by ViewControl to notify that a filter has been applied -- probably not used anymore
    
    def filter_applied(self, name) -> None:
        pass

    
    Called by ViewControl to notify that a filter reset -- probably not used anymore
    
    def filter_reset(self) -> None:
        pass
    """
    """
    Update the labels to reflect the current state
    """
    def update_labels(self) -> None:
        self.count_lbl.config(text=f'({self.stats.count_filtered(self.filter)} games selected, press Apply to apply)')
        #self.filter.print()

    """
    Get notified when an update occurs to a value and handle the update
    (for RangeAdjustors)
    """
    def update_range(self, name, which, value) -> None:
        if name == 'Loser Score':
            if which == 'min':
                self.filter.lose_score_min = value
                self.update_labels()
            elif which == 'max':
                self.filter.lose_score_max = value
                self.update_labels()
        elif name == 'Number':
            if which == 'min':
                self.filter.number_min = value
                self.update_labels()
            elif which == 'max':
                self.filter.number_max = value
                self.update_labels()

    """
    Get notified when an update occurs to a value and handle the update
    (for MultiSelectors)
    """
    def update_value(self, name, value):
        if name == 'Winner Select':
            self.filter.winners = set(value)
            self.update_labels()
        elif name == 'Loser Select':
            self.filter.losers = set(value)
            self.update_labels()
        elif name == 'Event Select':
            events = list[event_date.EventDate]()
            for event in value:
                events.append(self.events[event])
            self.filter.date_ranges = events
            self.update_labels()

"""
Interaction and visualization for creating graphs
"""
class GraphView(ttk.Frame):

    def __init__(self, frm:ttk.Frame, stats:sc.StatCollector):
        super().__init__(frm)
        
        self.frm = frm
        self.stats = stats

        self.supported_xs = ['date','number']
        self.supported_ys = ['wins','goals','colley win rank', 'colley goal rank', 'elo']

        self.players_to_show = MultiSelector(self,"Players",self.stats.list_players())
        self.players_to_show.add_listener(self)
        self.players_to_show.grid(row=0,column=0,sticky='news',rowspan=2)

        self.x_choice = SingleSelector(self,"x axis",self.supported_xs)
        self.x_choice.add_listener(self)
        self.x_choice.grid(row=0,column=1,sticky='news')

        self.y_choice = SingleSelector(self,"y axis",self.supported_ys)
        self.y_choice.add_listener(self)
        self.y_choice.grid(row=1,column=1,sticky='news')

        self.graph = graphsyousee.create_foosball_graph(f'{self.y_choice.get_selected()} by {self.x_choice.get_selected()}',self.x_choice.get_selected(),self.y_choice.get_selected(),
                                                        self.players_to_show.get_as_list(),
                                                        self.get_x_axis(),
                                                        self.get_y_axis())
        self.graph_display = FigureCanvasTkAgg(self.graph,self)
        self.graph_display.draw()
        self.graph_display.get_tk_widget().grid(row=0,column=2,sticky='news',rowspan=2)

    """
    
    """
    def update_value(self, name, value):
        # doesn't really matter what was updated, time to redraw the graph
        self.reset()

    def get_x_axis(self) -> list:
        choice = self.x_choice.get_selected()
        if choice == 'date':
            return self.stats.list_dates()
        elif choice == 'number':
            return self.stats.list_numbers()
        else:
            print(f"ERROR: unknown x axis {choice}")
        
    def get_y_axis(self) -> dict[str,list]:
        choice = self.y_choice.get_selected()
        if choice == 'wins':
            return graphsyousee.get_list_over_range(self.stats.filtered,self.get_x_axis(),self.players_to_show.get_as_list(),
                                                    lambda games:foosballgame.get_records(games),self.x_choice.get_selected()=='date',
                                                    lambda x: x[0])
        elif choice == 'goals':
            return graphsyousee.get_list_over_range(self.stats.filtered,self.get_x_axis(),self.players_to_show.get_as_list(),
                                                    lambda games:foosballgame.get_goals_scored_for_all(games),self.x_choice.get_selected()=='date',
                                                    lambda x: x[0])
        elif choice == 'colley win rank':
            return colley.get_rankings_list(self.stats.filtered,self.get_x_axis(),self.players_to_show.get_as_list(),
                                            is_daily=self.x_choice.get_selected()=='date',by_wins=True)
        elif choice == 'colley goal rank':
            return colley.get_rankings_list(self.stats.filtered,self.get_x_axis(),self.players_to_show.get_as_list(),
                                            is_daily=self.x_choice.get_selected()=='date',by_wins=False)
        elif choice == 'elo':
            return elo.get_rankings_list(self.stats.filtered,self.get_x_axis(),self.players_to_show.get_as_list(),
                                         is_daily=self.x_choice.get_selected()=='date')
        else:
            print(f"ERROR: unknown y axis {choice}")

    """
    Should update labels/check stats for any changes
    """ 
    def reset(self) -> None:
        matplotlib.pyplot.close(self.graph)
        self.graph_display.get_tk_widget().destroy()
        
        self.graph = graphsyousee.create_foosball_graph(f'{self.y_choice.get_selected()} by {self.x_choice.get_selected()}',self.x_choice.get_selected(),self.y_choice.get_selected(),
                                                        self.players_to_show.get_as_list(),
                                                        self.get_x_axis(),
                                                        self.get_y_axis())
        self.graph_display = FigureCanvasTkAgg(self.graph,self)
        self.graph_display.draw()
        self.graph_display.get_tk_widget().grid(row=0,column=2,sticky='news',rowspan=2)

    """
    Delete and recreate itself -- probably not needed
    """
    def reload(self) -> None:
        pass

    """
    Update labels to reflect current internal state -- no labels to update I think
    """
    def update_labels(self) -> None:
        pass

"""
Select values from a list of values
"""
class MultiSelector(ttk.Frame):

    def __init__(self, frm:ttk.Frame, name:str, options:list) -> None:
        super().__init__(frm, borderwidth=2, relief='groove')

        self.frm = frm
        self.name = name
        self.options = options

        self.listeners = []

        self.selected = list[tk.IntVar]()
        self.check_btns = list[ttk.Checkbutton]()

        r = 0
        ttk.Label(self,text=self.name).grid(row=r,column=0,columnspan=2)
        r += 1
        for option in self.options:
            self.selected.append(tk.IntVar())
            self.selected[-1].set(1)
            self.check_btns.append(ttk.Checkbutton(self, text=option, variable=self.selected[-1], onvalue=1, offvalue=0))
            self.check_btns[-1].state(['!alternate'])
            self.check_btns[-1].state(['selected'])
            self.check_btns[-1].grid(row=r,column=0,sticky='news')
            r += 1

        ttk.Button(self, text='Select All',   command=self.select_all).grid(row=1,column=1)
        ttk.Button(self, text='Deselect All', command=self.deselect_all).grid(row=2,column=1)
        ttk.Button(self, text='Apply',        command=self.value_update).grid(row=3,column=1)

    """
    Return the selected values as a list
    """
    def get_as_list(self) -> list[str]:
        lis = list[str]()
        for sel,opt in zip(self.selected,self.options):
            if sel.get() == 1:
                lis.append(opt)
        return lis

    """
    Notify any listeners that the values have been updated
    Passes the list of selected values to all listeners
    """
    def value_update(self) -> None:
        for listener in self.listeners:
            listener.update_value(self.name, self.get_as_list())

    """
    Selects all values
    """
    def select_all(self) -> None:
        for btn,sel in zip(self.check_btns,self.selected):
            btn.state(['selected'])
            sel.set(1)

    """
    Deselects all values
    """
    def deselect_all(self) -> None:
        for btn,sel in zip(self.check_btns,self.selected):
            btn.state(['!selected'])
            sel.set(0)

    """
    Adds a listener that will be updated everytime different values are selected
    Listeners use update_value(name, value) to listen
    """
    def add_listener(self, listener) -> None:
        self.listeners.append(listener)

"""
Select a value from a list of values
"""
class SingleSelector(ttk.Frame):

    def __init__(self, frm:ttk.Frame, name:str, options:list) -> None:
        super().__init__(frm, borderwidth=2, relief='groove')

        self.frm = frm
        self.name = name
        self.options = options

        self.listeners = []

        self.selected = tk.StringVar()

        r = 0
        ttk.Label(self,text=self.name).grid(row=r,column=0,columnspan=2)
        r += 1
        for option in self.options:
            ttk.Radiobutton(self, text=option, variable=self.selected, value=option).grid(row=r,column=0,sticky='news')
            r += 1
        self.selected.set(self.options[0])
        ttk.Button(self, text='Apply', command=self.value_update).grid(row=1,column=1)

    """
    Return the selected value
    """
    def get_selected(self) -> str:
        return self.selected.get()

    """
    Notify any listeners that the values have been updated
    Passes the list of selected values to all listeners
    """
    def value_update(self) -> None:
        for listener in self.listeners:
            listener.update_value(self.name, self.get_selected())

    """
    Adds a listener that will be updated everytime different values are selected
    Listeners use update_value(name, value) to listen
    """
    def add_listener(self, listener) -> None:
        self.listeners.append(listener)

"""
UI to adjust a range of values
"""
class RangeAdjustor(ttk.Frame):

    def __init__(self, frm:ttk.Frame, name:str, low_val:int=0, high_val:int=10, min_val:Union[int,None]=None, max_val:Union[int,None]=None):
        super().__init__(frm, borderwidth=2, relief='sunken')

        assert min_val <= low_val <= high_val <= max_val

        self.frm = frm
        self.name = name
        self.low_val = low_val
        self.high_val = high_val
        self.min_val = min_val
        self.max_val = max_val

        self.listeners = []

        r = 0
        ttk.Label(self,text=self.name,anchor='c').grid(row=r,column=1,sticky='news')
        r += 1
        self.min_adj = ValueAdjustor(self,'min',self.low_val,self.min_val,self.high_val)
        self.min_adj.grid(row=r,column=0,sticky='news')
        self.min_adj.add_listener(self)
        self.max_adj = ValueAdjustor(self,'max',self.high_val,self.low_val,self.max_val)
        self.max_adj.grid(row=r,column=2,sticky='news')
        self.max_adj.add_listener(self)

    """
    Adds a listener that will be notified when value is changed
    """
    def add_listener(self, listener) -> None:
        self.listeners.append(listener)

    """
    Updates the listeners based on a value change
    """
    def __update_listeners(self, which, value) -> None:
        for listener in self.listeners:
            listener.update_range(self.name, which, value)
    
    """
    Handles an update to one of the values
    """
    def update_value(self, name:str, value:int):
        if name == 'min':
            self.min_val = value
            self.max_adj.set_min(value)
        elif name == 'max':
            self.max_val = value
            self.min_adj.set_max(value)
        self.__update_listeners(name,value)


"""
UI to adjust a value with an optional min/max 
"""
class ValueAdjustor(ttk.Frame):
    
    def __init__(self, frm:ttk.Frame, name:str, cur_val:int=0, min_val:Union[int,None]=None, max_val:Union[int,None]=None) -> None:
        super().__init__(frm, borderwidth=2, relief='raised')

        assert min_val <= cur_val <= max_val

        self.frm = frm
        self.name = name
        self.value = cur_val
        self.max_val = max_val
        self.min_val = min_val

        self.listeners = []

        r = 0
        ttk.Label(self,text=self.name,anchor='c').grid(row=r,column=1,sticky='news')
        r += 1
        ttk.Button(self,text='-',command=self.decrease).grid(row=r,column=0,sticky='news')
        self.val_lbl = ttk.Label(self,text=self.value,anchor='c')
        self.val_lbl.grid(row=r,column=1,sticky='news')
        ttk.Button(self,text='+',command=self.increase).grid(row=r,column=2,sticky='news')

    """
    Adds a listener that will be notified when value is changed
    """
    def add_listener(self, listener) -> None:
        self.listeners.append(listener)

    """
    Updates lables to show current values
    """
    def update_labels(self) -> None:
        self.val_lbl.config(text=self.value)
        for listener in self.listeners:
            listener.update_value(self.name, self.value)

    """
    If it's within range, decreases the value and updates the label
    """
    def decrease(self) -> None:
        if self.min_val is None or self.value > self.min_val:
            self.value -= 1
            self.update_labels()

    """
    If it's withing range, increases the value and updates the label
    """
    def increase(self) -> None:
        if self.max_val is None or self.value < self.max_val:
            self.value += 1
            self.update_labels()

    """
    Sets the min value to a new value and updates the current value as necessary
    """
    def set_min(self, new_min:Union[int,None]) -> None:
        self.min_val = new_min
        if self.min_val is not None and self.min_val > self.value:
            self.value = self.min_val
            self.update_labels()

    """
    Sets the max value to a new value and updates the current value as necessary
    """
    def set_max(self, new_max:Union[int,None]) -> None:
        self.max_val = new_max
        if self.max_val is not None and self.max_val < self.value:
            self.value = self.max_val
            self.update_labels()



"""
#
Skeleton Class
#
class View(ttk.Frame):

    def __init__(self, frm:ttk.Frame, stats:sc.StatCollector):
        super().__init__(frm)
        
        self.frm = frm
        self.stats = stats

    #
    Should update labels/check stats for any changes
    #
    def reset(self) -> None:
        pass

    #
    Delete and recreate itself -- probably not needed
    #
    def reload(self) -> None:
        pass

    def update_labels(self) -> None:
        pass
"""