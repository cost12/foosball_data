import tkinter as tk
from tkinter import ttk

import statcollector as sc
import event_date

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
"""
class StatsViewControl(ttk.Frame):

    def __init__(self,frm:ttk.Frame,stats:sc.StatCollector,dates:list[event_date.EventDate]) -> None:
        super().__init__(frm)
        self.frm=frm

        self.stats = stats
        self.dates = dates
        self.view = str('table')
        self.views = {'table':StatTable(frm,stats),'sim':SimView(frm,stats)}

        self.add_buttons()

        self.views['table'].pack()
        self.views['sim'].pack()
        self.views['sim'].forget()

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

        # semester buttons
        filter_frm = ttk.Frame(self.frm)
        filter_frm.pack()
        filter_frm.columnconfigure(0,weight=1)
        def reset_filt():
            self.views[self.view].reset_filter()
        ttk.Button(filter_frm, text='All Time',command=reset_filt).grid(row=0,column=0)
        c=1
        for semester in self.dates:
            def filter(date=semester):
                self.views[self.view].filter_by_date(date)
            ttk.Button(filter_frm, text=semester.name,command=filter).grid(row=0,column=c)
            filter_frm.columnconfigure(c,weight=1)
            c+=1

    """
    Reload the current frame
    """
    def reload(self) -> None:
        self.views[self.view].reload()

    """
    Change from one frame to another
    """
    def change_view(self,view:str) -> None:
        if view in self.views and view != self.view:
            self.views[self.view].forget()
            self.view = view
            #self.views[self.view].tkraise()
            self.views[self.view].pack()

    """
    Repack the current frame
    """
    def repack(self) -> None:
        self.views[self.view].pack()

    #def add_view(self,name:str,view) -> None:
    #    self.views[name] = view

"""
Interaction and visulization for Simulator
"""
class SimView(ttk.Frame):

    def __init__(self,frm:ttk.Frame,stats:sc.StatCollector,p1:str='',p2:str='') -> None:
        super().__init__(frm)
        self.frm = frm
        
        self.stats = stats
        self.filtered_stats = stats

        self.time_str = 'All Time'

        self.player1=tk.StringVar()
        self.player2=tk.StringVar()
        self.set_simulator(init=True)

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

        # top row
        self.p1_ent = ttk.Entry(self,textvariable=self.player1)
        self.p1_ent.grid(row=0, column=0,sticky='news')
        self.p1_ent.insert(0,p1)
        self.reset_btn = ttk.Button(self, text='Reset', command=self.reset)
        self.reset_btn.grid(row=0, column=1,sticky='news')
        self.p2_ent = ttk.Entry(self,textvariable=self.player2)
        self.p2_ent.grid(row=0, column=2,sticky='news')
        self.p2_ent.insert(0,p2)

        # row 1
        self.score_lbl1 = ttk.Label(self, text='score:',anchor='e')
        self.score_lbl1.grid(row=1,column=0,sticky='news')
        self.sim_goal_btn = ttk.Button(self, text='Sim goal', command=self.sim_goal)
        self.sim_goal_btn.grid(row=1, column=1,sticky='news')
        self.score_lbl2 = ttk.Label(self, text='score:')
        self.score_lbl2.grid(row=1,column=2,sticky='news')

        # row 2
        self.score_num1 = ttk.Label(self, text=self.simulator.sim_score1,anchor='e')
        self.score_num1.grid(row=2,column=0,sticky='news')
        self.sim_game_btn = ttk.Button(self, text='Sim Game', command=self.sim_game)
        self.sim_game_btn.grid(row=2, column=1,sticky='news')
        self.score_num2 = ttk.Label(self, text=self.simulator.sim_score2)
        self.score_num2.grid(row=2,column=2,sticky='news')

        # row 3
        self.win_prob_lbl1 =  ttk.Label(self, text='win prob',anchor='e')
        self.win_prob_lbl1.grid(row=3,column=0,sticky='news')
        self.time_frame_lbl = ttk.Label(self, text=self.time_str,anchor='c')
        self.time_frame_lbl.grid(row=3,column=1,sticky='news')
        self.win_prob_lbl2 =  ttk.Label(self, text='win prob',anchor='w')
        self.win_prob_lbl2.grid(row=3,column=2,sticky='news')

        # row 4
        text = '{:>.3f}%'.format(self.simulator.get_p1_win_odds()*100)
        self.win_prob_num1 = ttk.Label(self, text=text,anchor='e')
        self.win_prob_num1.grid(row=4,column=0,sticky='news')
        text = '{:>.3f}%'.format((1-self.simulator.get_p1_win_odds())*100)
        self.win_prob_num2 = ttk.Label(self, text=text)
        self.win_prob_num2.grid(row=4,column=2,sticky='news')

        # row 5
        self.exp_score_lbl1 = ttk.Label(self, text='exp score',anchor='e')
        self.exp_score_lbl1.grid(row=5,column=0,sticky='news')
        self.exp_score_lbl2 = ttk.Label(self, text='exp score',anchor='w')
        self.exp_score_lbl2.grid(row=5,column=2,sticky='news')

        # row 6
        text = '{:>.3f}'.format(self.simulator.get_expected_score(self.simulator.player1))
        self.exp_score_num1 = ttk.Label(self, text=text,anchor='e')
        self.exp_score_num1.grid(row=6,column=0,sticky='news')
        text = '{:>.3f}'.format(self.simulator.get_expected_score(self.simulator.player2))
        self.exp_score_num2 = ttk.Label(self, text=text)
        self.exp_score_num2.grid(row=6,column=2,sticky='news')

        # row 7
        self.prob_score_lbl1 = ttk.Label(self, text='prob score',anchor='e')
        self.prob_score_lbl1.grid(row=7,column=0,sticky='news')
        self.prob_score_lbl2 = ttk.Label(self, text='prob score',anchor='w')
        self.prob_score_lbl2.grid(row=7,column=2,sticky='news')

        # row 8
        self.prob_score_num1 = ttk.Label(self, text=self.simulator.get_most_probable_score(self.simulator.player1),anchor='e')
        self.prob_score_num1.grid(row=8,column=0,sticky='news')
        self.prob_score_num2 = ttk.Label(self, text=self.simulator.get_most_probable_score(self.simulator.player2),anchor='w')
        self.prob_score_num2.grid(row=8,column=2,sticky='news')

        # row 9
        self.add_goal_btn1 = ttk.Button(self, text='Add Goal', command=lambda : self.add_goal(self.simulator.player1))
        self.add_goal_btn1.grid(row=9,column=0,sticky='news')
        self.add_goal_btn2 = ttk.Button(self, text='Add Goal', command=lambda : self.add_goal(self.simulator.player2))
        self.add_goal_btn2.grid(row=9,column=2,sticky='news')

        # row 10 (wins)
        #self.wins_lbl1 = ttk.Label()

        # row 11 (goals)
    
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
        self.set_simulator()

    """
    Reset the simulator and update the labels
    """
    def set_simulator(self,init:bool=False) -> None:
        self.simulator = self.filtered_stats.get_simulator(self.player1.get(),self.player2.get())
        if not init:
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
    def filter_by_date(self,date:event_date.EventDate) -> None:
        self.filtered_stats = self.stats.filter_by_date(date)
        self.time_str = date.name
        self.reset()

    """
    Reset the filter/ go back to games from all time frames
    """
    def reset_filter(self) -> None:
        self.filtered_stats = self.stats
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


"""
Interaction and visualization for StatCollector
"""
class StatTable(ttk.Frame):

    def __init__(self, frm:ttk.Frame, stats:sc.StatCollector, rmax:int=30, filtered:sc.StatCollector=None, sort:list[str]=['W PCT'], asc:bool=False, view:str='players') -> None:
        super().__init__(frm)
        
        self.frm = frm
        self.stats = stats
        if filtered is None:
            self.filtered_stats = self.stats
        else:
            self.filtered_stats = filtered
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
        self.__init__(self.frm,self.stats,self.rmax,self.filtered_stats,self.sort,self.ascending,self.view)
        self.pack()

    """
    Get data from the StatCollector and store it so it can be displayed
    """
    def get_data(self) -> None:
        data = self.filtered_stats.get_stats(self.view)
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
    def filter_by_date(self,date:event_date.EventDate) -> None:
        self.filtered_stats = self.stats.filter_by_date(date)
        self.reload()

    """ TODO: find a better way than reloading
    Reset the filter/ go back to games from all time frames
    """
    def reset_filter(self) -> None:
        self.filtered_stats = self.stats
        self.reload()







































"""
class ScrollableFrame(ttk.Frame):
    def __init__(self, parent, *args, **kw):
        ttk.Frame.__init__(self, parent, *args, **kw)

        # Create a canvas object and a vertical scrollbar for scrolling it.
        vscrollbar = ttk.Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                           yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # Reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # Create a frame inside the canvas which will be scrolled with it.
        self.scrollable_frame = interior = ttk.Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the canvas's width to fit the inner frame.
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # Update the inner frame's width to fill the canvas.
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)
"""