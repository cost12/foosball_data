from tkinter import *
from tkinter import ttk

import statcollector

def visualize_foosball(games,dates):
    root = Tk()
    root.rowconfigure(0,weight=1)
    root.columnconfigure(0,weight=1)

    stats = statcollector.StatCollector(games)
    viewControl = StatsViewControl(root,stats,dates)

    root.mainloop()


class StatsViewControl(ttk.Frame):

    def __init__(self,frm:ttk.Frame,stats:statcollector.StatCollector,dates):
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

    def add_buttons(self):
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
        ttk.Button(filter_frm, text='All Time',command=self.views['table'].reset_filter).grid(row=0,column=0)
        c=1
        for semester in self.dates:
            def filter(date=semester):
                return self.views['table'].filter_by_date(date)
            ttk.Button(filter_frm, text=semester.name,command=filter).grid(row=0,column=c)
            filter_frm.columnconfigure(c,weight=1)
            c+=1

    def reload(self):
        self.views[self.view].reload()

    def change_view(self,view:str) -> None:
        if view in self.views and view != self.view:
            self.views[self.view].forget()
            self.view = view
            #self.views[self.view].tkraise()
            self.views[self.view].pack()

    def repack(self):
        self.views[self.view].pack()

    #def add_view(self,name:str,view) -> None:
    #    self.views[name] = view

class SimView(ttk.Frame):

    def __init__(self,frm:ttk.Frame,sc:statcollector.StatCollector,p1='',p2=''):
        super().__init__(frm)
        self.frm = frm
        
        self.stats = sc
        self.player1=StringVar()
        self.player2=StringVar()
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

        # TODO: most of these 'variables' are None
        # top row
        self.p1_ent = ttk.Entry(self,textvariable=self.player1)
        self.p1_ent.grid(row=0, column=0,sticky='news')
        self.p1_ent.insert(0,p1)
        self.reset_btn = ttk.Button(self, text='Reset', command=self.reset).grid(row=0, column=1,sticky='news')
        self.p2_ent = ttk.Entry(self,textvariable=self.player2)
        self.p2_ent.grid(row=0, column=2,sticky='news')
        self.p2_ent.insert(0,p2)

        # row 1
        self.score_lbl1 = ttk.Label(self, text='score:',anchor='e').grid(row=1,column=0,sticky='news')
        self.sim_goal_btn = ttk.Button(self, text='Sim goal', command=self.sim_goal).grid(row=1, column=1,sticky='news')
        self.score_lbl2 = ttk.Label(self, text='score:').grid(row=1,column=2,sticky='news')

        # row 2
        self.score_num1 = ttk.Label(self, text=self.simulator.sim_score1,anchor='e')
        self.score_num1.grid(row=2,column=0,sticky='news')
        self.sim_game_btn = ttk.Button(self, text='Sim Game', command=self.sim_game).grid(row=2, column=1,sticky='news')
        self.score_num2 = ttk.Label(self, text=self.simulator.sim_score2)
        self.score_num2.grid(row=2,column=2,sticky='news')

        # row 3
        self.win_prob_lbl1 = ttk.Label(self, text='win prob',anchor='e').grid(row=3,column=0,sticky='news')
        self.win_prob_lbl2 = ttk.Label(self, text='win prob',anchor='w').grid(row=3,column=2,sticky='news')

        # row 4
        text = '{:>.3f}%'.format(self.simulator.get_p1_win_odds()*100)
        self.win_prob_num1 = ttk.Label(self, text=text,anchor='e')
        self.win_prob_num1.grid(row=4,column=0,sticky='news')
        text = '{:>.3f}%'.format((1-self.simulator.get_p1_win_odds())*100)
        self.win_prob_num2 = ttk.Label(self, text=text)
        self.win_prob_num2.grid(row=4,column=2,sticky='news')

        # row 5
        self.exp_score_lbl1 = ttk.Label(self, text='exp score',anchor='e').grid(row=5,column=0,sticky='news')
        self.exp_score_lbl2 = ttk.Label(self, text='exp score',anchor='w').grid(row=5,column=2,sticky='news')

        # row 6
        text = '{:>.3f}'.format(self.simulator.get_expected_score(self.simulator.player1))
        self.exp_score_num1 = ttk.Label(self, text=text,anchor='e')
        self.exp_score_num1.grid(row=6,column=0,sticky='news')
        text = '{:>.3f}'.format(self.simulator.get_expected_score(self.simulator.player2))
        self.exp_score_num2 = ttk.Label(self, text=text)
        self.exp_score_num2.grid(row=6,column=2,sticky='news')

        # row 7
        self.prob_score_lbl1 = ttk.Label(self, text='prob score',anchor='e').grid(row=7,column=0,sticky='news')
        self.prob_score_lbl2 = ttk.Label(self, text='prob score',anchor='w').grid(row=7,column=2,sticky='news')

        # row 8
        self.prob_score_num1 = ttk.Label(self, text=self.simulator.get_most_probable_score(self.simulator.player1),anchor='e')
        self.prob_score_num1.grid(row=8,column=0,sticky='news')
        self.prob_score_num2 = ttk.Label(self, text=self.simulator.get_most_probable_score(self.simulator.player2),anchor='w')
        self.prob_score_num2.grid(row=8,column=2,sticky='news')

        # row 9
        self.add_goal_btn1 = ttk.Button(self, text='Add Goal', command=lambda : self.add_goal(self.simulator.player1)).grid(row=9,column=0,sticky='news')
        self.add_goal_btn2 = ttk.Button(self, text='Add Goal', command=lambda : self.add_goal(self.simulator.player2)).grid(row=9,column=2,sticky='news')
    
        
    def reload(self):
        self.destroy()
        self.__init__(self.frm,self.sc,self.player1.get(),self.player2.get())
        self.pack()

    def reset(self):
        self.set_simulator()

    def set_simulator(self,init=False):
        self.simulator = self.stats.get_simulator(self.player1.get(),self.player2.get())
        if not init:
            self.update_labels()

    def sim_goal(self):
        self.simulator.simulate_goal()
        self.update_labels()

    def sim_game(self):
        self.simulator.simulate_game()
        self.update_labels()

    def add_goal(self,player):
        self.simulator.add_goal(player)
        self.update_labels()

    def update_labels(self):
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


class StatTable(ttk.Frame):

    def __init__(self, frm:ttk.Frame, sc:statcollector.StatCollector, rmax=30,filtered=None,sort=['W PCT'],asc=False,view='players'):
        super().__init__(frm)
        
        self.frm = frm
        self.stats = sc
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
        r += 2
        c=0
        for stat in self.stats.list_stats():
            def set_v(v=stat):
                self.set_view(v)
            btn = ttk.Button(self, text=stat,command=set_v)
            btn.grid(row=r,column=c,sticky='news')
            c += 1


    def reload(self):
        self.destroy()
        self.__init__(self.frm,self.stats,self.rmax,self.filtered_stats,self.sort,self.ascending,self.view)
        self.pack()

    def get_data(self):
        data = self.filtered_stats.get_stats(self.view)
        for sort in self.sort:
            if sort not in data.columns:
                self.sort.remove(sort)
        if len(self.sort)>0:
            data = data.sort_values(by=self.sort, ascending=self.ascending)
        return data

    def sort_by(self, n, ascending=None):
        if n in self.sort:
            self.sort.remove(n)
        self.sort.insert(0,n)
        if ascending is not None:
            self.ascending = ascending
        self.reload()

    def __sort_call(self, n):
        ascending = self.ascending
        if len(self.sort) > 0 and self.sort[0] == n:
            ascending = not self.ascending
        return lambda:self.sort_by(n,ascending)

    def set_view(self, view):
        if self.view != view:
            self.view = view
            self.reload()

    def filter_by_date(self,date):
        self.filtered_stats = self.stats.filter_by_date(date)
        self.reload()

    def reset_filter(self):
        self.filtered_stats = self.stats
        self.reload()

