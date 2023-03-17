from tkinter import *
from tkinter import ttk
import math

import statcollector

def visualize_foosball(games,dates):
    root = Tk()
    root.rowconfigure(0,weight=1)
    root.columnconfigure(0,weight=1)

    stats = statcollector.StatCollector(games)

    # sim setup
    #sset_frm = ttk.Frame(root)
    #sset_frm.grid(sticky='news')
    #sim_setup = SimSetup(sset_frm,stats)

    # sim display
    sim_frm = ttk.Frame(root)
    sim_frm.grid(sticky='news')
    sim_view = SimView(sim_frm,stats)

    # stat display
    stat_frm = ttk.Frame(root)
    stat_frm.grid(sticky='news')

    stat_tbl = StatTable(stat_frm,stats)
    stat_tbl.set_view('players')
    stat_tbl.sort_by('W PCT',False)
    
    # view buttons
    btn_frm = ttk.Frame(root)
    btn_frm.grid(sticky='news')
    c=0
    for stat in stats.list_stats():
        def change_view(view=stat):
            return stat_tbl.set_view(view)
        btn = ttk.Button(btn_frm, text=stat,command=change_view)
        btn.grid(row=0,column=c,sticky='news')
        c += 1

    # semester buttons
    sem_frm = ttk.Frame(root)
    sem_frm.grid(sticky='news')
    btn = ttk.Button(sem_frm, text='All Time',command=stat_tbl.reset_filter)
    btn.grid(row=0,column=0,sticky='news')
    c=0
    for semester in dates:
        def filter(date=semester):
            return stat_tbl.filter_by_date(date)
        btn = ttk.Button(sem_frm, text=semester.name,command=filter)
        btn.grid(row=0,column=c+1,sticky='news')
        c += 1
    
    views = {'stats':stat_tbl,'sim':sim_view} #, 'sim setup':sim_setup}

    # screen buttons
    scr_btn_frm = ttk.Frame(root)
    scr_btn_frm.grid(sticky='news')
    c=0
    for scr in views.keys():
        def change_view(v=scr):
            for view in views:
                views[view].destroy()
            view = v
            views[v].reload()
        btn = ttk.Button(scr_btn_frm,text=scr,command=change_view)
        btn.grid(row=0,column=c,sticky='news')
        c += 1

    root.mainloop()


class SimView:

    def __init__(self,frm,sc:statcollector.StatCollector,p1='',p2=''):
        self.frm = frm
        self.stats = sc
        #self.sim_set = sim_set

        self.labels = []
        self.buttons = []
        self.entries = []

        self.player1=p1
        self.player2=p2
        self.set_simulator()

    def set_players(self):
        if len(self.entries) > 1:
            self.player1 = self.entries[0].get()
            self.player2 = self.entries[1].get()
        self.set_simulator()

    def set_simulator(self):
        self.simulator = self.stats.get_simulator(self.player1,self.player2)

    def sim_goal(self):
        self.simulator.simulate_goal()
        self.__display()

    def sim_game(self):
        self.simulator.simulate_game()
        self.__display()

    def add_goal(self,player):
        self.simulator.add_goal(player)
        self.__display()

    def reload(self):
        self.set_players()
        self.set_simulator()
        self.__display()

    def __display(self):
        self.destroy()

        self.frm.columnconfigure(0,weight=5)
        self.frm.columnconfigure(1,weight=1)
        self.frm.columnconfigure(2,weight=5)
        self.frm.rowconfigure(0,weight=2)
        self.frm.rowconfigure(1,weight=1)
        self.frm.rowconfigure(2,weight=2)
        self.frm.rowconfigure(3,weight=1)
        self.frm.rowconfigure(4,weight=1)
        self.frm.rowconfigure(5,weight=1)
        self.frm.rowconfigure(6,weight=1)
        self.frm.rowconfigure(7,weight=1)
        self.frm.rowconfigure(8,weight=1)
        self.frm.rowconfigure(9,weight=1)

        # top row
        ent = ttk.Entry(self.frm)
        ent.insert(0,self.player1)
        ent.grid(row=0, column=0,sticky='news')
        self.entries.append(ent)

        btn = ttk.Button(self.frm, text='Reset', command=self.reload)
        btn.grid(row=0, column=1,sticky='news')
        self.buttons.append(btn)

        ent = ttk.Entry(self.frm)
        ent.insert(0,self.player2)
        ent.grid(row=0, column=2,sticky='news')
        self.entries.append(ent)

        # row 1
        lbl = ttk.Label(self.frm, text='score:',anchor='e')
        lbl.grid(row=1,column=0,sticky='news')
        self.labels.append(lbl)

        btn = ttk.Button(self.frm, text='Sim goal', command=self.sim_goal)
        btn.grid(row=1, column=1,sticky='news')
        self.buttons.append(btn)

        lbl = ttk.Label(self.frm, text='score:')
        lbl.grid(row=1,column=2,sticky='news')
        self.labels.append(lbl)

        # row 2
        lbl = ttk.Label(self.frm, text=self.simulator.sim_score1,anchor='e')
        lbl.grid(row=2,column=0,sticky='news')
        self.labels.append(lbl)

        btn = ttk.Button(self.frm, text='Sim Game', command=self.sim_game)
        btn.grid(row=2, column=1,sticky='news')
        self.buttons.append(btn)

        lbl = ttk.Label(self.frm, text=self.simulator.sim_score2)
        lbl.grid(row=2,column=2,sticky='news')
        self.labels.append(lbl)

        # row 3
        lbl = ttk.Label(self.frm, text='win prob',anchor='e')
        lbl.grid(row=3,column=0,sticky='news')
        self.labels.append(lbl)

        lbl = ttk.Label(self.frm, text='win prob')
        lbl.grid(row=3,column=2,sticky='news')
        self.labels.append(lbl)

        # row 4
        text = '{:>.3f}%'.format(self.simulator.get_p1_win_odds()*100)
        lbl = ttk.Label(self.frm, text=text,anchor='e')
        lbl.grid(row=4,column=0,sticky='news')
        self.labels.append(lbl)

        text = '{:>.3f}%'.format((1-self.simulator.get_p1_win_odds())*100)
        lbl = ttk.Label(self.frm, text=text)
        lbl.grid(row=4,column=2,sticky='news')
        self.labels.append(lbl)

        # row 5
        lbl = ttk.Label(self.frm, text='exp score',anchor='e')
        lbl.grid(row=5,column=0,sticky='news')
        self.labels.append(lbl)

        lbl = ttk.Label(self.frm, text='exp score')
        lbl.grid(row=5,column=2,sticky='news')
        self.labels.append(lbl)

        # row 6
        text = '{:>.3f}'.format(self.simulator.get_expected_score(self.simulator.player1))
        lbl = ttk.Label(self.frm, text=text,anchor='e')
        lbl.grid(row=6,column=0,sticky='news')
        self.labels.append(lbl)

        text = '{:>.3f}'.format(self.simulator.get_expected_score(self.simulator.player2))
        lbl = ttk.Label(self.frm, text=text)
        lbl.grid(row=6,column=2,sticky='news')
        self.labels.append(lbl)

        # row 7
        lbl = ttk.Label(self.frm, text='prob score',anchor='e')
        lbl.grid(row=7,column=0,sticky='news')
        self.labels.append(lbl)

        lbl = ttk.Label(self.frm, text='prob score')
        lbl.grid(row=7,column=2,sticky='news')
        self.labels.append(lbl)

        # row 8
        lbl = ttk.Label(self.frm, text=self.simulator.get_most_probable_score(self.simulator.player1),anchor='e')
        lbl.grid(row=8,column=0,sticky='news')
        self.labels.append(lbl)

        lbl = ttk.Label(self.frm, text=self.simulator.get_most_probable_score(self.simulator.player2))
        lbl.grid(row=8,column=2,sticky='news')
        self.labels.append(lbl)

        # row 9
        btn = ttk.Button(self.frm, text='Add Goal', command=lambda : self.add_goal(self.simulator.player1))
        btn.grid(row=9,column=0,sticky='news')
        self.buttons.append(btn)

        btn = ttk.Button(self.frm, text='Add Goal', command=lambda : self.add_goal(self.simulator.player2))
        btn.grid(row=9,column=2,sticky='news')
        self.buttons.append(btn)

    def destroy(self):
        for lbl in self.labels:
            lbl.destroy()
        self.labels = []
        for btn in self.buttons:
            btn.destroy()
        self.buttons = []
        for ent in self.entries:
            ent.destroy()
        self.entries = []

class SimSetup:

    def __init__(self,frm,sc):
        self.frm = frm
        self.stats = sc

        self.labels = []
        self.entries = []

        self.p1_selected=''
        self.p2_selected=''

    def reload(self):
        self.__display()

    def __display(self):
        self.destroy()

        self.frm.columnconfigure(0,weight=1)
        self.frm.columnconfigure(1,weight=1)
        self.frm.rowconfigure(0,weight=1)
        self.frm.rowconfigure(1,weight=1)

        lbl = ttk.Label(self.frm, text='Player 1', anchor='e')
        lbl.grid(row=0, column=0,sticky='news')
        self.labels.append(lbl)

        lbl = ttk.Label(self.frm, text='Player 2', anchor='e')
        lbl.grid(row=0, column=1,sticky='news')
        self.labels.append(lbl)

        ent = ttk.Entry(self.frm)
        ent.grid(row=1,column=0,sticky='news')
        self.entries.append(ent)

        ent = ttk.Entry(self.frm)
        ent.grid(row=1,column=1,sticky='news')
        self.entries.append(ent)

    def destroy(self):
        if len(self.entries) > 1:
            self.player1 = self.entries[0].get()
            self.player2 = self.entries[1].get()
        for lbl in self.labels:
            lbl.destroy()
        self.labels = []
        for ent in self.entries:
            ent.destroy()
        self.entries = []

class StatTable:

    def __init__(self, frm, sc, rmax=30):
        self.stat_frm = frm
        self.stats = sc
        self.filtered_stats = self.stats
        self.sort = []
        self.ascending = True
        self.view = None
        self.labels = []
        self.buttons = []
        self.rmax = rmax
        
        self.color = 'black'
        self.highlight = 'white'
        self.font  = 'arial'
        self.background = 'gray'
        self.font_size = 16
        self.width = 10
        self.relief = 'ridge'

    def reload(self):
        self.__display()

    def __display(self):
        self.destroy()
        data = self.get_data()

        self.stat_frm.columnconfigure(0,weight=1)
        self.stat_frm.rowconfigure(0,weight=1)
        # headers
        for c in range(len(data.columns)):
            self.stat_frm.columnconfigure(c+1,weight=1) # for filling vertically
            header = data.columns[c]
            #btn = ttk.Button(self.stat_frm, text=header,command=self.__sort_call(header),background=self.background,width=self.width-1,relief=self.relief,fg=self.color,font=(self.font,self.font_size,'bold'))
            btn = ttk.Button(self.stat_frm, text=header,command=self.__sort_call(header),width=self.width-1)
            btn.grid(row=0, column=c+1,sticky='news')
            self.buttons.append(btn)

        for r in range(min(data.shape[0],self.rmax)):
            self.stat_frm.rowconfigure(r+1,weight=1) # for filling horizontally
            # numbers
            width = 1+int(math.log10(len(data)))
            #lbl = ttk.Label(self.stat_frm, text=r+1, anchor='e',width=width,background=self.background,relief=self.relief,fg=self.color,font=(self.font,self.font_size,'bold'))
            lbl = ttk.Label(self.stat_frm, text=r+1, anchor='e',width=width)
            lbl.grid(row=r+1, column=0,sticky='news')
            self.labels.append(lbl)

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
                #lbl = ttk.Label(self.stat_frm, text=data.iloc[r][c], anchor=anchor,width=self.width,background=background,relief=self.relief,fg=self.color,font=(self.font,self.font_size,'bold'))
                lbl = ttk.Label(self.stat_frm, text=text, anchor=anchor,width=self.width,background=background)
                lbl.grid(row=r+1, column=c+1,sticky='news')
                self.labels.append(lbl)

    def destroy(self):
        for lbl in self.labels:
            lbl.destroy()
        self.labels = []
        for btn in self.buttons:
            btn.destroy()
        self.buttons = []

    def get_data(self):
        data = self.filtered_stats.get_stats(self.view)
        if set(self.sort).issubset(data.columns):
            data = data.sort_values(by=self.sort, ascending=self.ascending)
        else:
            self.sort = []
        return data

    def sort_by(self, n, ascending=None):
        if n in self.sort:
            self.sort.remove(n)
        self.sort.insert(0,n)
        if ascending is not None:
            self.ascending = ascending
        self.__display()

    def __sort_call(self, n):
        ascending = self.ascending
        if len(self.sort) > 0 and self.sort[0] == n:
            ascending = not self.ascending
        return lambda:self.sort_by(n,ascending)

    def set_view(self, view):
        if self.view != view:
            self.view = view
            self.__display()

    def filter_by_date(self,date):
        self.filtered_stats = self.stats.filter_by_date(date)
        self.__display()

    def reset_filter(self):
        self.filtered_stats = self.stats
        self.__display()

