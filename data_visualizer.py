import tkinter as tk
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import datetime

import data_read_in
import statcollector as sc
import event_date
import gamefilter
import graphsyousee
import foosballgame
import colley
import elo
import myranks
import individual
import utils
import simulator
from visual_tools import *
import constants as c
import records

from urllib.error import URLError

"""
Main loop for tkinter
"""
def visualize_foosball() -> None:
    try:
        games_options = data_read_in.read_in_games_options()
    except Exception as e:
        print("No options available for games")
        print(e)
        return
    
    try:
        dates_options = data_read_in.read_in_dates_options()
    except Exception as e:
        print("No options available for dates")
        print(e)
        return

    root = tk.Tk()
    #root.rowconfigure(0,weight=1)
    #root.columnconfigure(0,weight=1)

    s = ttk.Style()
    #s.configure(root, font=('Tahoma', 11)) # Calibri

    viewControl = StatsViewControl(root,games_options,dates_options)

    root.mainloop()

"""
Super class for all views/screens
"""
class View(ttk.Frame):

    def __init__(self, frm:ttk.Frame, *, __s:sc.StatCollector=None, __d:list[utils.SheetIdentifier]=None, __f:gamefilter.GameFilter=None):
        super().__init__(frm)
        
        self.frm = frm
        self.attached = False

        self.attached = bool(False)
        self.stats = __s
        self.dates = __d
        self.filter = __f


    """
    View attaches to the stats and dates passed in, updates it's values according to stats and dates
    """
    def attach(self, stats, dates, filter) -> None:
        raise NotImplementedError()

    """
    View detaches from stats and dates and will no longer reflect changes stats or dates
    """
    def detach(self) -> None:
        raise NotImplementedError()

    """
    Should update labels/check stats for any changes
    """
    def reset(self) -> None:
        raise NotImplementedError()

    """
    Updates the labels to reflect changes to stats or dates
    """
    def update_labels(self) -> None:
        raise NotImplementedError()
    
    """
    Determines wether the view has completed all necessary actions to allow a change of screens
    """
    def ready_to_leave(self) -> bool:
        return True

"""
Decides which frames are displayed

Attaches and detaches views from stats and dates, sometimes has to update stats and dates

Displays to add
 - records
 - leagues
 - individual
 - news/legends
"""
class StatsViewControl(ttk.Frame):

    def __init__(self,frm:ttk.Frame,games_options:list[utils.SheetIdentifier],dates_options:list[utils.SheetIdentifier]) -> None:
        super().__init__(frm)
        self.frm=frm

        start_screen = str('dataset')

        self.stats = sc.StatCollector([])
        self.dates = list[event_date.EventDate]()
        self.filter = gamefilter.GameFilter()
        
        self.view = start_screen
        self.views = dict[str, View] ( \
                     {#'info':       InfoScreen(frm),
                      'dataset':    DataSelector(frm, games_options, dates_options),
                      'filter':     FilterView(frm),
                      'table':      StatTable(frm),
                      'sim':        SimView(frm),
                      'graphs':     GraphView(frm), #TODO: implement these/ come up with more
                      #'individual': IndividualView(frm),
                      #'legends':    [],
                      'records':    RecordsView(frm),
                      #'overview':   [],
                      #'leauges':    [],
                      #'game_entry': [],
                      } \
        )
        self.no_game_views = ['dataset', 'filter']
        
        self.buttons = ButtonGroup(self.frm, "Screens", list(self.views.keys()),selected=start_screen)
        self.buttons.add_listener(self)
        self.buttons.pack()

        self.error_text = tk.StringVar()
        self.error_text.set("Welcome!")
        ttk.Label(self.frm,textvariable=self.error_text).pack()#fill='y',expand=True,side='top')

        for view in self.views:
            self.views[view].pack(fill='y',expand=True,side='top')
        for view in self.views:
            if not view == start_screen:
                self.views[view].forget()
        self.views[start_screen].attach(self.stats, self.dates, self.filter)

    """
    Called by the buttons to change the screen
    """
    def update_value(self, name, value):
        if name == 'Screens':
            self.change_view(value)

    """
    Change from one frame to another
    """
    def change_view(self,view:str) -> None:
        if len(self.stats.filtered) == 0 and view not in self.no_game_views:
            self.error_text.set("Error: No games selected")
            self.buttons.set_highlight(self.view)
            return
        if not self.views[self.view].ready_to_leave():
            self.error_text.set("Error: Can't leave yet")
            self.buttons.set_highlight(self.view)
            return
        if view in self.views and view != self.view:
            self.error_text.set("No Errors Detected")
            self.views[self.view].forget()
            self.views[self.view].detach()
            self.view = view
            self.views[self.view].attach(self.stats, self.dates, self.filter)
            self.views[self.view].pack(fill='y',expand=True,side='top')

"""
Select which datasets will be loaded and used
"""
class DataSelector(View):

    def __init__(self, frm:ttk.Frame, games_options:list[utils.SheetIdentifier], dates_options:list[utils.SheetIdentifier]):
        super().__init__(frm)
    
        self.games_dict = dict[str,utils.SheetIdentifier]()
        for option in games_options:
            self.games_dict[option.name] = option

        self.dates_dict = dict[str,utils.SheetIdentifier]()
        for option in dates_options:
            self.dates_dict[option.name] = option

        self.first_games = games_options[0].name
        self.first_dates = dates_options[0].name

        self.games_select = SingleSelector(self, 'Games Selection', [x.name for x in games_options], apply_btn=True)
        self.games_select.add_listener(self)
        self.games_select.grid(row=0,column=0,sticky='news')

        self.dates_select = SingleSelector(self, 'Dates Selection', [x.name for x in dates_options], apply_btn=True)
        self.dates_select.add_listener(self)
        self.dates_select.grid(row=0,column=1,sticky='news')

        self.error_text = tk.StringVar()
        self.error_text.set("Waiting for a place to load data... you probably shouldn't see this")
        ttk.Label(self,textvariable=self.error_text).grid(row=1,column=0,columnspan=2,sticky='news')

        self.selected_games = LabeledValue(self, 'Game Dataset In Use')
        self.selected_dates = LabeledValue(self, 'Date Dataset In Use')

        self.selected_games.grid(row=2,column=0,sticky='news')
        self.selected_dates.grid(row=2,column=1,sticky='news')

        self.games_picked = False
        self.dates_picked = False

    def ready_to_leave(self) -> bool:
        return self.games_picked and self.dates_picked

    """
    Updates the current selection of data/ dates
    """
    def update_value(self, name, value):
        if not self.attached:
            return
        
        # need a loading screen here

        success = True
        if name == 'Dates Selection':
            sheet = self.dates_dict[value]
            date_fnf = False
            date_bad_format = False
            try:
                dates = data_read_in.read_in_dates_from_sheets(sheet.id, sheet.sheet_name)
                self.error_text.set('Date file loaded successfully')
            except URLError as fnf:
                date_fnf = True
                self.error_text.set('Date file not found, looking for csv instead...')
            except ValueError as ve:
                date_bad_format = True
                self.error_text.set('Date file has incorrect format, loading from csv instead...')
            finally:
                if date_fnf or date_bad_format:
                    try:
                        dates = data_read_in.read_in_dates_from_csv(sheet.csv_name)
                        self.error_text.set(self.error_text.get() + '\ncsv loaded successfully')
                    except FileNotFoundError as fnf:
                        success = False
                        self.error_text.set(self.error_text.get() + '\ncsv not found, data load unsuccessful')
                    except ValueError as ve:
                        success = False
                        self.error_text.set(self.error_text.get() + '\ncsv has incorrect format, data load unsuccessful')
            if success:
                self.dates_picked = True
                self.dates.clear()
                self.dates.extend(dates)
                selected_txt = value
                if date_fnf or date_bad_format:
                    selected_txt += ' (local)'
                self.selected_dates.set_value(selected_txt)
        elif name == 'Games Selection':
            sheet = self.games_dict[value]
            game_fnf = False
            game_bad_format = False
            try:
                games = data_read_in.read_in_games_from_sheets(sheet.id, sheet.sheet_name)
                self.error_text.set('Game file loaded successfully')
            except URLError as fnf:
                game_fnf = True
                self.error_text.set('Game file not found, looking for csv instead...')
            except ValueError as ve:
                game_bad_format = True
                self.error_text.set('Game file has incorrect format, loading from csv instead...')
            finally:
                if game_fnf or game_bad_format:
                    try:
                        games = data_read_in.read_in_games_from_csv(sheet.csv_name)
                        self.error_text.set(self.error_text.get() + '\ncsv loaded successfully')
                    except FileNotFoundError as fnf:
                        print(fnf)
                        game_csv_fnf = True
                        self.error_text.set(self.error_text.get() + '\ncsv not found, data load unsuccessful')
                        success = False
                    except ValueError as ve:
                        print(ve)
                        game_csv_bad_format = True
                        self.error_text.set(self.error_text.get() + '\ncsv has incorrect format, data load unsuccessful')
                        success = False
            if success:
                self.games_picked = True
                self.filter.reset()
                self.stats.set_games(games)
                selected_txt = value
                if game_fnf or game_bad_format:
                    selected_txt += ' (local)'
                self.selected_games.set_value(selected_txt)

        # exit loading screen
        

    def attach(self, stats:sc.StatCollector, dates:list[event_date.EventDate], filter:gamefilter.GameFilter):
        if not self.attached:
            self.attached = True
            self.stats = stats
            self.dates = dates
            self.filter = filter
            self.error_text.set('Select data then press Apply to load')
            # this shouldn't select the first thing every time, that would be expensive and annoying
            # instead only update for the first load, then just make sure the right things are selected
            # alternatively, just have a button - press to load
            #self.update_value('Games Selection', self.first_games)
            #self.update_value('Dates Selection', self.first_dates)
            # this should actually work

    def detach(self):
        self.attached = False
        self.stats = None
        self.dates = None
        self.filter = None
    
    """
    Should update labels/check stats for any changes
    """
    def reset(self) -> None:
        pass

    def update_labels(self) -> None:
        pass

"""
Interaction and visulization for Simulator
"""
class SimView(View):

    def __init__(self,frm:ttk.Frame,*,p1:str='',p2:str='') -> None:
        super().__init__(frm)        

        self.show_probs = True

        self.player1=tk.StringVar()
        self.player2=tk.StringVar()
        # TODO: simulator should be something that gets passed into attach
        self.simulator = simulator.get_simulator(self.player1.get(),self.player2.get(), 'prob' if self.show_probs else 'skill')

        top_frm = ttk.Frame(self)

        selector = SingleSelector(top_frm,'Simulation Type',['Probability','Skill'])
        selector.add_listener(self)
        selector.grid(row=0,column=0,sticky='news')
        self.is_skill = False

        self.goal_points = ValueAdjustor(top_frm, 'Goals to Win', 10, 1, None)
        self.goal_points.add_listener(self)
        self.goal_points.grid(row=0,column=1,sticky='news')

        top_frm.grid(row=0,column=0,columnspan=3,sticky='news')

        r = 1
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
        self.time_frame_lbl = ttk.Label(self, text='Cool!',anchor='c')
        self.time_frame_lbl.grid(row=r,column=1,sticky='news')
        self.win_prob_lbl2 =  ttk.Label(self, text='win prob',anchor='w')
        self.win_prob_lbl2.grid(row=r,column=2,sticky='news')

        r += 1
        # row 4
        text = '0' #'{:>.3f}%'.format(self.simulator.get_p1_win_odds()*100)
        self.win_prob_num1 = ttk.Label(self, text=text,anchor='e')
        self.win_prob_num1.grid(row=r,column=0,sticky='news')
        text = '0' #'{:>.3f}%'.format((1-self.simulator.get_p1_win_odds())*100)
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
        text = '0' #'{:>.3f}'.format(self.simulator.get_expected_score(self.simulator.player1))
        self.exp_score_num1 = ttk.Label(self, text=text,anchor='e')
        self.exp_score_num1.grid(row=r,column=0,sticky='news')
        text = '0' #'{:>.3f}'.format(self.simulator.get_expected_score(self.simulator.player2))
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
        self.prob_score_num1 = ttk.Label(self, text='0',anchor='e')#self.simulator.get_most_probable_score(self.simulator.player1),anchor='e')
        self.prob_score_num1.grid(row=r,column=0,sticky='news')
        self.prob_score_num2 = ttk.Label(self, text='0',anchor='w')#self.simulator.get_most_probable_score(self.simulator.player2),anchor='w')
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

        self.row_count = r

        self.score_lbls_p1 = []
        self.score_lbls_num= []
        self.score_lbls_p2 = []
        for i in range(0,11):
            r += 1
            p1_lbl = ttk.Label(self, text=0, anchor='e')
            p1_lbl.grid(row=r,column=0,sticky='news')
            num_lbl = ttk.Label(self,text=i,anchor='c')
            num_lbl.grid(row=r,column=1,sticky='news')
            p2_lbl = ttk.Label(self, text=0, anchor='w')
            p2_lbl.grid(row=r,column=2,sticky='news')

            self.score_lbls_p1.append(p1_lbl)
            self.score_lbls_num.append(num_lbl)
            self.score_lbls_p2.append(p2_lbl)

    def attach(self, stats:sc.StatCollector, dates:list[event_date.EventDate], filter=None):
        if not self.attached:
            self.attached = True
            self.stats = stats
            self.dates = dates
            self.simulator.attach(self.stats)
            self.update_labels()

    def detach(self):
        self.attached = False
        self.stats = None
        self.dates = None

        self.simulator.detach()

    """
    Resets the simulator
    """
    def reset(self) -> None: # TODO: there must be a better way to do this
        self.simulator = simulator.get_simulator(self.player1.get(),self.player2.get(),'skill' if self.is_skill else 'prob')
        self.simulator.attach(self.stats)
        self.goal_points.set_value(10)
        #self.update_labels() - auto called by previous line

    def update_value(self, name:str, value):
        if name == 'Simulation Type':
            if value == 'Probability':
                self.is_skill = False
            else:
                self.is_skill = True
            self.reset()
        elif name == 'Goals to Win':
            self.simulator.set_game_to(value)
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
    Updates the labels with new information from the simulation
    """
    def update_labels(self) -> None:
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
            rows_used = self.simulator.game_to+1
            for i in range(0,rows_used):
                if i < len(self.score_lbls_num):
                    text = '{:>.3f}'.format(self.simulator.get_prob_of_score(self.simulator.player1,i)*100)
                    self.score_lbls_p1[i].config(text=text)
                    text = '{:>.3f}'.format(self.simulator.get_prob_of_score(self.simulator.player2,i)*100)
                    self.score_lbls_p2[i].config(text=text)
                else:
                    r = self.row_count+i+1
                    text = '{:>.3f}'.format(self.simulator.get_prob_of_score(self.simulator.player1,i)*100)
                    p1_lbl = ttk.Label(self, text=text, anchor='e')
                    p1_lbl.grid(row=r,column=0,sticky='news')
                    num_lbl = ttk.Label(self,text=i,anchor='c')
                    num_lbl.grid(row=r,column=1,sticky='news')
                    text = '{:>.3f}'.format(self.simulator.get_prob_of_score(self.simulator.player2,i)*100)
                    p2_lbl = ttk.Label(self, text=text, anchor='w')
                    p2_lbl.grid(row=r,column=2,sticky='news')

                    self.score_lbls_p1.append(p1_lbl)
                    self.score_lbls_num.append(num_lbl)
                    self.score_lbls_p2.append(p2_lbl)
        else: # show results
            rows_used = 10 + 1
            for i in range(0,rows_used):
                if i < len(self.score_lbls_num):
                    self.score_lbls_p1[i].config(text=self.simulator.get_times_scored_n(self.simulator.player1,i))
                    self.score_lbls_p2[i].config(text=self.simulator.get_times_scored_n(self.simulator.player2,i))
                else:
                    r = self.row_count+i
                    p1_lbl = ttk.Label(self, text=self.simulator.get_times_scored_n(self.simulator.player1,i), anchor='e')
                    p1_lbl.grid(row=r,column=0,sticky='news')
                    num_lbl = ttk.Label(self,text=i,anchor='c')
                    num_lbl.grid(row=r,column=1,sticky='news')
                    p2_lbl = ttk.Label(self, text=self.simulator.get_times_scored_n(self.simulator.player2,i), anchor='w')
                    p2_lbl.grid(row=r,column=2,sticky='news')

                    self.score_lbls_p1.append(p1_lbl)
                    self.score_lbls_num.append(num_lbl)
                    self.score_lbls_p2.append(p2_lbl)
        for i in range(rows_used,len(self.score_lbls_num)):
            self.score_lbls_p1[i].destroy()
            self.score_lbls_num[i].destroy()
            self.score_lbls_p2[i].destroy()
        self.score_lbls_p1 = self.score_lbls_p1[0:rows_used]
        self.score_lbls_num= self.score_lbls_num[0:rows_used]
        self.score_lbls_p2 = self.score_lbls_p2[0:rows_used]
            
"""
Interaction and visualization for StatCollector
"""
class StatTable(View):

    def __init__(self, frm:ttk.Frame, rmax:int=25, sort:list[str]=['W PCT'], asc:bool=False, view:str='standings') -> None:
        super().__init__(frm)
                
        self.sort = sort
        self.ascending = asc
        self.view = view
        self.max_rows = rmax
        self.start_row = 0
        self.num_rows = 0
        
        self.highlight = 'white'
        self.background = 'gray'

        self.labels = list[list[ttk.Label]]()
        self.buttons = list[ttk.Button]()
        self.view_btns = ButtonGroup(self, 'Views')
        self.view_btns.add_listener(self)
        self.end_btns = list[ttk.Button]()

    def attach(self, stats:sc.StatCollector, dates=None, filter=None):
        if not self.attached:
            self.attached = True
            self.stats = stats

            r=0
            c=0
            stat_opts = self.stats.list_stats()
            self.view_btns.set_options(stat_opts, self.view)
            self.view_btns.grid(row=r+2,column=c,columnspan=len(stat_opts)+1,sticky='news')
            c += len(stat_opts)+1
            btn = ttk.Button(self,text='prev',command=self.prev_page)
            btn.grid(row=r+2,column=c+1,sticky='news')
            self.end_btns.append(btn)
            btn = ttk.Button(self,text='next',command=self.next_page)
            btn.grid(row=r+2,column=c+2,sticky='news')
            self.end_btns.append(btn)

            self.update_labels()

    def update_value(self, name, value):
        if name == 'Views':
            self.set_view(value)

    def detach(self):
        self.attached = False
        self.stats = None

        self.start_row = 0
        self.num_rows = 0

        self.view_btns.set_options([])

        for button in self.end_btns:
            button.destroy()
        self.end_btns.clear()
        for button in self.buttons:
            button.destroy()
        self.buttons.clear()
        for lis in self.labels:
            for label in lis:
                label.destroy()
            lis.clear()
        self.labels.clear()

    """
    Called to update labels quickly
    """
    def reset(self) -> None:
        self.start_row = 0
        self.update_labels()

    """ TODO: error because sometimes the gap between prev and the previous thing does not exist
    Update the table values without having to delete/ redraw
    """
    def update_labels(self) -> None:
        if not self.attached:
            return
        # get the data
        data = self.get_data()
        prev_rows = self.num_rows
        prev_cols = len(self.buttons)
        self.num_rows = min(data.shape[0]-self.start_row,self.max_rows)

        # create the buttons on the top row
        for c in range(len(data.columns)):
            header = data.columns[c]
            if c < len(self.buttons):
                self.buttons[c].config(text=header,command=self.__sort_call(header))
            else:
                btn = ttk.Button(self, text=header,command=self.__sort_call(header))
                btn.grid(row=0, column=c+1,sticky='news')
                self.buttons.append(btn)

        # remove excess from buttons and labels
        len_btns = c+1                   # the number of current buttons
        if len(self.buttons) > len_btns: # max(current buttons, prev buttons) > current buttons (there are an excess that need to be removed)
            # delete labels
            for r in range(len(self.labels)):
                for c in range(len_btns,len(self.buttons)):
                    self.labels[r][c+1].destroy() # +1 because of number labels
                self.labels[r] = self.labels[r][:c+1]
            # delete buttons
            for c in range(len_btns,len(self.buttons)):
                self.buttons[c].destroy()
            self.buttons = self.buttons[:len_btns]

        for r in range(self.num_rows):
            # number any new rows created, make sure all number labels have the correct number
            if r >= prev_rows:
                nlbl = ttk.Label(self, text=self.start_row+r+1, anchor='e')
                nlbl.grid(row=r+1, column=0,sticky='news')

                self.labels.append([])
                self.labels[-1].append(nlbl)
            else:
                self.labels[r][0].config(text=self.start_row+r+1)
            # highlight columns if needed, format text correctly, add label if needed
            for c in range(len(data.iloc[r])):
                background = self.background
                if len(self.sort) > 0 and self.sort[0] == data.columns[c]:
                    background = self.highlight
                text = data.iloc[r+self.start_row][c]
                anchor = 'e'
                if isinstance(text,str):
                    anchor = 'w'
                if isinstance(text,float):
                    text = '{:>.3f}'.format(text)
                if r < prev_rows and c < prev_cols:
                    self.labels[r][c+1].config(text=text,background=background,anchor=anchor)
                else:
                    lbl = ttk.Label(self, text=text,background=background,anchor=anchor)
                    lbl.grid(row=r+1, column=c+1,sticky='news')
                    self.labels[r].insert(c+1, lbl)
        # remove excess rows and number labels
        if self.num_rows < prev_rows:
            for r in range(self.num_rows,prev_rows):
                for lbl in self.labels[r]:
                    lbl.destroy()
            self.labels = self.labels[:self.num_rows]
        elif self.num_rows > prev_rows:
            # move the bottom row of buttons to the new bottom
            c = 0
            self.view_btns.grid(row=self.num_rows+2,column=c,columnspan=len(self.view_btns.options)+1,sticky='news')
            c += len(self.view_btns.options) + 2
            for btn in self.end_btns:
                btn.grid(row=self.num_rows+2,column=c,sticky='news')
                c += 1

    """
    Advance to the next page/ see more stats
    """
    def next_page(self) -> None:
        if self.num_rows >= self.max_rows:
            self.start_row += self.max_rows
            self.update_labels()

    """
    Go back to the previous page
    """
    def prev_page(self) -> None:
        if self.start_row > 0:
            self.start_row = max(self.start_row-self.max_rows,0)
            self.update_labels()

    """
    Get data from the StatCollector and store it so it can be displayed
    """
    def get_data(self) -> pd.DataFrame:
        data = self.stats.get_stats(self.view)
        for s in self.sort:
            if s not in data.columns:
                self.sort.remove(s)
                if c.DEBUG_MODE:
                    print("removed " + s)
        if len(self.sort)>0:
            try:
                data = data.sort_values(by=self.sort, ascending=self.ascending)
            except:
                if c.DEBUG_MODE:
                    print(data.columns)
                    print(self.sort)
                    print("")
        return data

    """
    Sets the main sort to be n and the direction is decided by ascending
    Calls reset so that the data is displayed as sorted
    """
    def sort_by(self, n:str, ascending:bool=None) -> None:
        if n in self.sort:
            self.sort.remove(n)
        self.sort.insert(0,n)
        if ascending is not None:
            self.ascending = ascending
        self.reset()

    """
    This is called when a button is clicked to sort the data
    Returns a lambda function that calls sort_by and passes in n and the correct direction
    """
    def __sort_call(self, n:str): # TODO: figure out how to type hint this
        ascending = self.ascending
        if len(self.sort) > 0 and self.sort[0] == n:
            ascending = not self.ascending
        return lambda:self.sort_by(n,ascending)

    """
    Change the view to a different stat category
    """
    def set_view(self, view:str) -> None:
        if self.view != view:
            self.view = view
            self.reset()

"""
Interaction and visualization for a filter
"""
class FilterView(View):

    def __init__(self, frm:ttk.Frame) -> None:
        super().__init__(frm)

        self.date_lookup = dict[str,event_date.EventDate]()

        self.count_text = tk.StringVar()
        self.count_text.set('(0 games selected)')
        ttk.Label(self, textvariable=self.count_text).grid(row=0,column=0,columnspan=4,sticky='news')

        self.winner_select = MultiSelector(self, 'Winner Select')
        self.winner_select.add_listener(self)
        self.winner_select.grid(row=1,column=0,rowspan=4,sticky='news')

        self.loser_select = MultiSelector(self, 'Loser Select')
        self.loser_select.add_listener(self)
        self.loser_select.grid(row=1,column=1,rowspan=4,sticky='news')

        self.restrict_select = MultiSelector(self, 'Restrict', ['restrict'])
        self.restrict_select.add_listener(self)
        self.restrict_select.grid(row=5,column=0,columnspan=2,sticky='news')

        self.event_select = MultiSelector(self, 'Event Select')
        self.event_select.add_listener(self)
        self.event_select.grid(row=1,column=2,rowspan=2,sticky='news')

        self.loser_score_range = RangeAdjustor(self, 'Loser Score')
        self.loser_score_range.add_listener(self)
        self.loser_score_range.grid(row=1,column=3,sticky='news')

        self.number_range = RangeAdjustor(self, 'Number')
        self.number_range.add_listener(self)
        self.number_range.grid(row=2,column=3,sticky='news')

        ttk.Button(self,text='Apply',command=self.apply_filter).grid(row=4,column=2,sticky='news')
        #ttk.Button(self,text='Reset',command=self.reset_filter).grid(row=4,column=3,sticky='news')

    def attach(self, stats:sc.StatCollector, dates:list[event_date.EventDate], filter:gamefilter.GameFilter):
        if not self.attached:
            self.attached = True
            self.stats = stats
            self.dates = dates
            self.filter = filter

            for date in self.dates:
                self.date_lookup[date.name] = date
            self.update_options()

    def update_options(self): # TODO: make sure filter and visualization are matched
        self.winner_select.set_options(self.stats.list_players())
        self.loser_select.set_options(self.stats.list_players())
        self.event_select.set_options(list(self.date_lookup.keys()))
        
        self.loser_score_range.set_min_val(self.stats.min_score_possible())
        self.loser_score_range.set_max_val(self.stats.max_score_possible())
        
        self.number_range.set_min_val(self.stats.min_num())
        self.number_range.set_max_val(self.stats.max_num())

        if self.filter.initialized:
            self.winner_select.deselect_all(like_click=False)
            for player in self.filter.winners:
                self.winner_select.select(player, like_click=False)

            self.loser_select.deselect_all(like_click=False)
            for player in self.filter.losers:
                self.loser_select.select(player, like_click=False)

            self.event_select.deselect_all(like_click=False)
            for event in self.filter.date_ranges:
                self.event_select.select(event.name, like_click=False)

            self.loser_score_range.set_low_val(self.filter.lose_score_min)
            self.loser_score_range.set_high_val(self.filter.lose_score_max)

            self.number_range.set_low_val(self.filter.number_min)
            self.number_range.set_high_val(self.filter.number_max)

            if self.filter.restrict:
                self.restrict_select.select_all(like_click=False)
            else:
                self.restrict_select.deselect_all(like_click=False)
        else:
            self.filter.winners.clear()
            self.filter.winners.update(self.winner_select.options)

            self.filter.losers.clear()
            self.filter.losers.update(self.loser_select.options)

            self.filter.date_ranges.clear()
            self.filter.date_ranges.extend(list(self.date_lookup.values()))

            self.loser_score_range.set_low_val(self.stats.min_score_loss())
            self.loser_score_range.set_high_val(self.stats.max_score_loss())

            self.number_range.set_low_val(self.stats.min_num_selected())
            self.number_range.set_high_val(self.stats.max_num_selected())

            self.restrict_select.select_all()
            self.filter.restrict = True
            self.filter.initialized = True

    def detach(self):
        self.attached = None
        self.stats = None
        self.dates = None
        self.filter = None

        self.date_lookup.clear()

        self.winner_select.clear_options()
        self.loser_select.clear_options()
        self.event_select.clear_options()

    """
    Called by ViewControl
    """
    def reset(self) -> None:
        pass

    """
    Apply the chosen filter to the stats
    """
    def apply_filter(self) -> None:
        self.stats.apply_filter(self.filter)
        #self.update_options()
        self.count_text.set(f'({self.stats.count_filtered(self.filter)} games selected)')

    """
    Reset the stats to the default filter
    """
    def reset_filter(self) -> None: #TODO: actually reset or just remove
        self.stats.reset_filter()
        #self.update_options()
        self.count_text.set(f'({self.stats.count_filtered(self.filter)} games selected)')

    """
    Update the labels to reflect the current state
    """
    def update_labels(self) -> None:
        self.count_text.set(f'({self.stats.count_filtered(self.filter)} games selected, press Apply to apply)')

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
        elif name == 'Loser Select':
            self.filter.losers = set(value)
        elif name == 'Event Select':
            events = list[event_date.EventDate]()
            for event in value:
                events.append(self.date_lookup[event])
            self.filter.date_ranges = events
        elif name == 'Restrict':
            self.filter.restrict = (len(value)==1)
        else:
            return # only update labels if something happens
        self.update_labels()

"""
Interaction and visualization for creating graphs
"""
class GraphView(View):

    def __init__(self, frm:ttk.Frame):
        super().__init__(frm)
        
        self.supported_xs = ['date','number','game']
        self.supported_ys = ['wins','goals','colley win rank', 'colley goal rank', 'elo', 'skill']

        self.players_to_show = MultiSelector(self,"Players")
        self.players_to_show.add_listener(self)
        self.players_to_show.grid(row=0,column=0,sticky='news',rowspan=3)

        self.x_choice = SingleSelector(self,"x axis",self.supported_xs)
        self.x_choice.add_listener(self)
        self.x_choice.grid(row=0,column=1,sticky='news')

        self.y_choice = SingleSelector(self,"y axis",self.supported_ys)
        self.y_choice.add_listener(self)
        self.y_choice.grid(row=1,column=1,sticky='news')

        self.alpha_val = ValueAdjustor(self,'alpha',0.5,0,1,0.05)
        self.alpha_val.add_listener(self)
        self.alpha_val.grid(row=2,column=1,sticky='news')

        self.graphed = False
        # TODO: this may cause an error, may be unecessary, leave in?
        """
        self.graph = graphsyousee.create_foosball_graph(f'{self.y_choice.get_selected()} by {self.x_choice.get_selected()}',self.x_choice.get_selected(),self.y_choice.get_selected(),
                                                        self.players_to_show.get_as_list(),
                                                        self.get_x_axis(),
                                                        self.get_y_axis())
        self.graph_display = FigureCanvasTkAgg(self.graph,self)
        self.graph_display.draw()
        self.graph_display.get_tk_widget().grid(row=2,column=1,sticky='news',rowspan=3)
        """

    def attach(self, stats:sc.StatCollector, dates=None, filter=None) -> None:
        if not self.attached:
            self.attached = True
            self.stats = stats

            self.players_to_show.set_options(self.stats.list_players())
            self.reset()

    def detach(self):
        self.attached = False
        self.stats = None

        self.players_to_show.clear_options()

        if self.graphed:
            matplotlib.pyplot.close(self.graph)
            self.graph_display.get_tk_widget().destroy()
        self.graphed = False

    """
    
    """
    def update_value(self, name, value):
        # doesn't really matter what was updated, time to redraw the graph
        self.reset()

    def get_x_cutoffs(self) -> list:
        choice = self.x_choice.get_selected()
        if choice == 'date':
            return self.stats.list_dates()
        elif choice in ['number','game']:
            return self.stats.list_numbers()
        else:
            print(f"ERROR: unknown x axis {choice}")

    def get_x_axis(self) -> list:
        choice = self.x_choice.get_selected()
        if choice == 'date':
            return self.stats.list_dates()
        elif choice == 'number':
            return self.stats.list_numbers()
        elif choice == 'game':
            return list(range(len(self.stats.list_numbers())))
        else:
            print(f"ERROR: unknown x axis {choice}")
        
    def get_y_axis(self) -> dict[str,list]:
        choice = self.y_choice.get_selected()
        if choice == 'wins':
            return graphsyousee.get_list_over_range(self.stats.filtered,self.get_x_cutoffs(),self.players_to_show.get_as_list(),
                                                    lambda games:foosballgame.get_records(games),self.x_choice.get_selected()=='date',
                                                    lambda x: x[0])
        elif choice == 'goals':
            return graphsyousee.get_list_over_range(self.stats.filtered,self.get_x_cutoffs(),self.players_to_show.get_as_list(),
                                                    lambda games:foosballgame.get_goals_scored_for_all(games),self.x_choice.get_selected()=='date',
                                                    lambda x: x[0])
        elif choice == 'colley win rank':
            return colley.get_rankings_list(self.stats.filtered,self.get_x_cutoffs(),self.players_to_show.get_as_list(),
                                            is_daily=self.x_choice.get_selected()=='date',by_wins=True)
        elif choice == 'colley goal rank':
            return colley.get_rankings_list(self.stats.filtered,self.get_x_cutoffs(),self.players_to_show.get_as_list(),
                                            is_daily=self.x_choice.get_selected()=='date',by_wins=False)
        elif choice == 'elo':
            return elo.get_rankings_list(self.stats.filtered,self.get_x_cutoffs(),self.players_to_show.get_as_list(),
                                         is_daily=self.x_choice.get_selected()=='date')
        elif choice == 'skill':
            return myranks.get_rankings_list(self.stats.filtered,self.get_x_cutoffs(),self.players_to_show.get_as_list(),
                                             is_daily=self.x_choice.get_selected()=='date',syst=myranks.SkillRating,name='Skill',alpha=self.alpha_val.value)
        else:
            print(f"ERROR: unknown y axis {choice}")

    """
    Should update labels/check stats for any changes
    """ 
    def reset(self) -> None:
        if self.graphed:
            matplotlib.pyplot.close(self.graph)
            self.graph_display.get_tk_widget().destroy()
        self.graphed = True
        
        self.graph = graphsyousee.create_foosball_graph(f'{self.y_choice.get_selected()} by {self.x_choice.get_selected()}',self.x_choice.get_selected(),self.y_choice.get_selected(),
                                                        self.players_to_show.get_as_list(),
                                                        self.get_x_axis(),
                                                        self.get_y_axis())
        self.graph_display = FigureCanvasTkAgg(self.graph,self)
        self.graph_display.draw()
        self.graph_display.get_tk_widget().grid(row=0,column=2,sticky='news',rowspan=3)

    """
    Update labels to reflect current internal state -- no labels to update I think
    """
    def update_labels(self) -> None:
        pass

"""
Display records accumulated across different time frames
"""
class RecordsView(View):

    def __init__(self, frm:ttk.Frame):
        super().__init__(frm)

        self.records = records.Records()

        record_list = list[tuple[str,str]]()
        for category in self.records.get_categories():
            record_list.append((category, "None"))

        self.groups = dict[str,LabelGroup]()
        i = 0
        for time_frame in self.records.get_time_frames():
            self.groups[time_frame] = LabelGroup(self, time_frame.upper(), record_list)
            self.groups[time_frame].grid(row=i//2,column=i%2,sticky='news')
            i += 1

    def attach(self, stats:sc.StatCollector, dates:list[event_date.EventDate], filter) -> None:
        if not self.attached:
            self.stats = stats
            self.dates = dates
            self.attached = True
            self.records.attach(self.stats, self.dates) # TODO: only pass in semesters?
            self.update_labels()

    def detach(self) -> None:
        self.stats = None
        self.dates = None
        self.attached = False
        self.records.detach()

    def reset(self) -> None:
        pass
    
    # TODO: this -> need to fill out the records class first though
    def update_labels(self) -> None:
        for time_frame in self.groups.keys():
            for category in self.records.get_categories():
                record = self.records.get_record(category,time_frame)
                record_str = ""
                for player in record[1]:
                    if 'day' in time_frame:
                        record_str += f'{record[0]} {player[0]} ({player[1].strftime("%b %#d, %y")})\n'
                    elif 'semester' in time_frame:
                        record_str += f'{record[0]} {player[0]} ({player[1]})\n'
                    else:
                        record_str += f'{record[0]} {player}\n'
                record_str = record_str[:-1]
                self.groups[time_frame].set_value(category, record_str)


""" TODO: this whole class
Interaction and visualization for individual achievements
"""
class IndividualView(View):

    def __init__(self, frm:ttk.Frame):
        super().__init__(frm)
        
        self.individual = individual.IndividualStats('',self.stats)

        entry_frm = ttk.Frame(self)
        entry_frm.grid(row=0,column=0,sticky='news')
        ttk.Label(entry_frm,text='Name').grid(row=0,column=0,sticky='news')
        self.player = tk.StringVar()
        ttk.Entry(entry_frm,textvariable=self.player).grid(row=0,column=1,sticky='news')
        ttk.Button(entry_frm,text='Apply',command=self.update_labels).grid(row=0,column=2,sticky='news')

        stats_frm = ttk.Frame(self)
        stats_frm.grid(row=1,column=0,sticky='news')
        ttk.Label(stats_frm,text='Wins').grid(row=0,column=0,sticky='news')
        self.wins = ttk.Label(stats_frm,text=0)
        self.wins.grid(row=1,column=0,sticky='news')
        ttk.Label(stats_frm,text='Losses').grid(row=0,column=1,sticky='news')
        self.losses = ttk.Label(stats_frm,text=0)
        self.losses.grid(row=1,column=1,sticky='news')

        ttk.Label(stats_frm,text='Goals For').grid(row=0,column=2,sticky='news')
        self.gf = ttk.Label(stats_frm,text=0)
        self.gf.grid(row=1,column=2,sticky='news')
        ttk.Label(stats_frm,text='Goals Against').grid(row=0,column=3,sticky='news')
        self.ga = ttk.Label(stats_frm,text=0)
        self.ga.grid(row=1,column=3,sticky='news')

    def attach(self, stats, dates, filter) -> None:
        pass

    def detach(self) -> None:
        pass

    """
    Should update labels/check stats for any changes
    """
    def reset(self) -> None:
        pass

    def update_labels(self) -> None:
        pass

def main() -> None:
    visualize_foosball()

if __name__ == "__main__":
    main()