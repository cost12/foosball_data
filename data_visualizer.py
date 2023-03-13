from tkinter import *
from tkinter import ttk
import math

import statcollector

def visualize_foosball(games):
    root = Tk()
    root.rowconfigure(0,weight=1)
    root.columnconfigure(0,weight=1)

    display_frm = ttk.Frame(root)
    display_frm.grid(sticky='news')

    stats = statcollector.StatCollector(games)
    stat_tbl = StatTable(display_frm,stats)
    stat_tbl.set_view('players')
    stat_tbl.sort_by('W PCT',False)
    
    btn_frm = ttk.Frame(root)
    btn_frm.grid(sticky='news')
    c=0
    for stat in stats.list_stats():
        def change_view(view=stat):
            return stat_tbl.set_view(view)
        btn = ttk.Button(btn_frm, text=stat,command=change_view)
        btn.grid(row=0,column=c,sticky='news')
        c += 1
    
    root.mainloop()


class StatTable:

    def __init__(self, frm, sc):
        self.stat_frm = frm
        self.stats = sc
        self.sort = []
        self.ascending = True
        self.view = None
        self.labels = []
        self.buttons = []
        
        self.color = 'black'
        self.highlight = 'white'
        self.font  = 'arial'
        self.background = 'gray'
        self.font_size = 16
        self.width = 10
        self.relief = 'ridge'

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

        for r in range(data.shape[0]):
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
        data = self.stats.get_stats(self.view)
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

