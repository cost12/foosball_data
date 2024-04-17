import tkinter as tk
from tkinter import ttk
from tkinter.constants import *
import platform

from typing import Union

import constants as c
import foosballgame
import tournament
import records

""" TODO: should duplicates be allowed? right now they are
Select values from a list of values
"""
class MultiSelector(ttk.Frame):

    def __init__(self, frm:ttk.Frame, name:str, options:list[str] = None,*, max_len:int=20, apply_btn:bool=False, sorted:bool=True) -> None:
        super().__init__(frm, borderwidth=2, relief='groove')

        self.frm = frm
        self.name = name
        if options is None:
            self.options = list[str]()
        else:
            self.options = options
        self.apply_btn = apply_btn
        self.sorted = sorted
        self.max_len = max_len

        self.listeners = []

        self.selected = list[tk.IntVar]()
        self.check_btns = list[ttk.Checkbutton]()

        ttk.Label(self,text=self.name).grid(row=0,column=0,columnspan=2,sticky='news')
        self.__place_buttons()

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
    def select_all(self, like_click:bool=True) -> None:
        for btn,sel in zip(self.check_btns,self.selected):
            btn.state(['selected'])
            sel.set(1)
        if not self.apply_btn and like_click:
            self.value_update()

    """
    Deselects all values
    """
    def deselect_all(self, like_click:bool=True) -> None:
        for btn,sel in zip(self.check_btns,self.selected):
            btn.state(['!selected'])
            sel.set(0)
        if not self.apply_btn and like_click:
            self.value_update()

    """
    Adds a listener that will be updated everytime different values are selected
    Listeners use update_value(name, value) to listen
    """
    def add_listener(self, listener) -> None:
        self.listeners.append(listener)

    def select(self, option:str, like_click:bool=True) -> bool:
        if option in self.options:
            self.check_btns[self.options.index(option)].state(['selected'])
            self.selected[self.options.index(option)].set(1)
            if not self.apply_btn and like_click:
                self.value_update()
            return True
        return False

    def deselect(self, option:str, like_click:bool=True) -> bool:
        if option in self.options:
            if self.selected[self.options.index(option)]:
                self.check_btns[self.options.index(option)].state(['!selected'])
                self.selected[self.options.index(option)].set(0)
            if not self.apply_btn and like_click:
                self.value_update()
            return True
        return False

    def clear_options(self) -> None:
        for button in self.check_btns:
            button.destroy()
        self.check_btns.clear()
        self.options.clear()
        self.selected.clear()

    """
    def remove_option(self, option:str) -> bool:
        if option in self.options:
            index = self.options.index(option)
            btn = self.check_btns.pop(index)
            btn.destroy()
            self.options.pop(index)
            self.selected.pop(index)
            for i in range(index,len(self.check_btns)):
                btn.grid(row=i%20,column=i//20,sticky='news')
            return True
        return False
    """
        
    """
    def add_option(self, option:str, select:bool=True) -> None:
        if self.sorted:
            if c.DEBUG_MODE:
                print("Error: Multiselector.add_option not implemented for sorted selections")
        else:
            self.options.append(option)
            self.selected.append(tk.IntVar(value=0))
            if self.apply_btn:
                self.check_btns.append(ttk.Checkbutton(self, text=option, variable=self.selected[-1], onvalue=1, offvalue=0))
            else:
                self.check_btns.append(ttk.Checkbutton(self, text=option, variable=self.selected[-1], onvalue=1, offvalue=0, command=self.value_update))
            self.check_btns[-1].state(['!alternate'])
            if select:
                self.check_btns[-1].state(['selected'])
                self.selected[-1].set(1)
            r = len(self.options)%self.max_len
            c = len(self.options)//self.max_len
            self.check_btns[-1].grid(row=r,column=c,sticky='news')
    """

    def add_options(self, options:list[str]) -> None:
        for option in options:
            self.add_option(option)

    def set_options(self, options:list[str]) -> None:
        self.clear_options()
        self.options.extend(options)
        self.__place_buttons()

    def __place_buttons(self):
        r=0
        if self.sorted:
            self.options.sort()
        for option in self.options:
            self.selected.append(tk.IntVar())
            if self.apply_btn:
                self.check_btns.append(ttk.Checkbutton(self, text=option, variable=self.selected[-1], onvalue=1, offvalue=0))
            else:
                self.check_btns.append(ttk.Checkbutton(self, text=option, variable=self.selected[-1], onvalue=1, offvalue=0, command=self.value_update))
            self.check_btns[-1].state(['!alternate'])
            self.check_btns[-1].state(['selected'])
            self.selected[-1].set(1)
            r2 = r%self.max_len + 1
            c = r//self.max_len
            self.check_btns[-1].grid(row=r2,column=c,sticky='news')
            r += 1

        c = r//self.max_len + 1
        self.end_btns = []
        b1 = ttk.Button(self, text='Select All',   command=self.select_all)
        b1.grid(row=1,column=c,sticky='news')
        self.end_btns.append(b1)

        b2 = ttk.Button(self, text='Deselect All', command=self.deselect_all)
        b2.grid(row=2,column=c,sticky='news')
        self.end_btns.append(b2)

        if self.apply_btn:
            b3 = ttk.Button(self, text='Apply', command=self.value_update)
            b3.grid(row=3,column=c,sticky='news')
            self.end_btns.append(b3)

""" TODO: should duplicates be allowed? right now they are
Select a value from a list of values
"""
class SingleSelector(ttk.Frame):

    def __init__(self, frm:ttk.Frame, name:str, options:list, *, selected:str=None, apply_btn:bool=False, sorted:bool=True) -> None:
        super().__init__(frm, borderwidth=2, relief='groove')

        self.frm = frm
        self.name = name
        self.options = options
        self.apply_btn = apply_btn
        self.sorted = sorted

        self.listeners = []

        self.selected = tk.StringVar()
        self.btns = list[ttk.Radiobutton]()

        ttk.Label(self,text=self.name).grid(row=0,column=0,columnspan=2,sticky='news')
        self.__place_buttons()

        if self.apply_btn:
            ttk.Button(self, text='Apply', command=self.value_update).grid(row=len(self.options)+1,column=0,columnspan=2,sticky='news')
        if selected is not None and selected in self.options:
            self.selected.set(selected)

    def __place_buttons(self):
        if self.sorted:
            self.options.sort()
        r = 1
        for option in self.options:
            if self.apply_btn:
                self.btns.append(ttk.Radiobutton(self, text=option, variable=self.selected, value=option))
            else:
                self.btns.append(ttk.Radiobutton(self, text=option, variable=self.selected, value=option, command=self.value_update))
            self.btns[-1].grid(row=r,column=0,sticky='news')
            r += 1
        self.selected.set(self.options[0])

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

    def select(self, option:str, like_click:bool=True) -> bool:
        if option in self.options:
            self.selected.set(option)
            if not self.apply_btn and like_click:
                self.value_update()
            return True
        return False

    def clear_options(self) -> None:
        for button in self.btns:
            button.destroy()
        self.btns.clear()
        self.options.clear()
        self.selected.set('')

    def remove_option(self, option:str) -> bool:
        if option in self.options:
            index = self.options.index(option)
            btn = self.btns.pop(index)
            btn.destroy()
            self.options.pop(index)
            for i in range(index,len(self.btns)):
                btn.grid(row=i,column=0,sticky='news')
            if self.selected.get() == option:
                if len(self.btns) > 0:
                    self.selected.set(self.options[0])
                    self.value_update()
                else:
                    self.selected.set('')
            return True
        return False
    
    def add_option(self, option:str) -> None:
        if self.sorted:
            if c.DEBUG_MODE:
                print("Error: Multiselector.add_option not implemented for sorted selections")
        else:
            self.options.append(option)
            if self.apply_btn:
                self.btns.append(ttk.Radiobutton(self, text=option, variable=self.selected, value=option))
            else:
                self.btns.append(ttk.Radiobutton(self, text=option, variable=self.selected, value=option, command=self.value_update))
            self.btns[-1].grid(row=len(self.options),column=0,sticky='news')

    def add_options(self, options:list[str]) -> None:
        for option in options:
            self.add_option(option)

    def set_options(self, options:list[str]) -> None:
        self.clear_options()
        self.options.extend(options)
        self.__place_buttons()

"""
UI to adjust a range of values
"""
class RangeAdjustor(ttk.Frame):

    def __init__(self, frm:ttk.Frame, name:str, low_val:int=0, high_val:int=10, min_val:Union[int,None]=None, max_val:Union[int,None]=None,*,plus_minus_btns=False,jump=1):
        super().__init__(frm, borderwidth=2, relief='sunken')

        assert ((min_val is not None and min_val <= low_val and low_val <= high_val) or (min_val is None and low_val <= high_val))  and (max_val is not None and high_val <= max_val or max_val is None)

        self.frm = frm
        self.name = name
        self.low_val = low_val
        self.high_val = high_val
        self.min_val = min_val
        self.max_val = max_val

        self.listeners = []

        r = 0
        ttk.Label(self,text=self.name,anchor='c').grid(row=r,column=0,columnspan=2,sticky='news')
        r += 1
        self.min_adj = ValueAdjustor(self,'min',self.low_val,self.min_val,self.high_val,plus_minus_btns=plus_minus_btns,jump=jump)
        self.min_adj.grid(row=r,column=0,sticky='news')
        self.min_adj.add_listener(self)
        self.max_adj = ValueAdjustor(self,'max',self.high_val,self.low_val,self.max_val,plus_minus_btns=plus_minus_btns,jump=jump)
        self.max_adj.grid(row=r,column=1,sticky='news')
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
    ValueAdjustor calls this when a value is changed
    """
    def update_value(self, name:str, value:int):
        if name == 'min':
            self.min_val = value
            self.max_adj.set_min(value)
        elif name == 'max':
            self.max_val = value
            self.min_adj.set_max(value)
        self.__update_listeners(name,value)

    def set_min_val(self, value):
        self.min_val = value
        self.min_adj.set_min(value)

    def set_max_val(self, value):
        self.max_val = value
        self.max_adj.set_max(value)

    def set_low_val(self, value):
        self.low_val = value
        self.min_adj.set_value(value)

    def set_high_val(self, value):
        self.high_val = value
        self.max_adj.set_value(value)

"""
UI to adjust a value with an optional min/max 
"""
class ValueAdjustor(ttk.Frame):
    
    def __init__(self, frm:ttk.Frame, name:str, cur_val:float=0, min_val:Union[float,None]=None, max_val:Union[float,None]=None,*, is_int:bool=True, apply_btn=False, plus_minus_btns=False,jump=1) -> None:
        super().__init__(frm, borderwidth=2, relief='raised')

        assert ((min_val is not None and min_val <= cur_val) or min_val is None) and ((max_val is not None and cur_val <= max_val) or max_val is None)

        self.frm = frm
        self.name = name
        self.max_val = max_val
        self.min_val = min_val
        self.is_int = is_int
        self.apply_btn = apply_btn

        self.listeners = []

        r = 0
        ttk.Label(self,text=self.name,anchor='c').grid(row=r,column=0,columnspan=2,sticky='news')
        r += 1
        if is_int:
            self.val = tk.IntVar()
        else:
            self.val = tk.DoubleVar()
        self.val.set(cur_val)
        ttk.Entry(self,textvariable=self.val).grid(row=r,column=1,sticky='news')
        ttk.Button(self,text='Update',command=self.update_labels).grid(row=r,column=2)#,sticky='news')
        r+=1
        if self.apply_btn:
            ttk.Button(self,text='Apply',command=self.notify_listeners).grid(row=r,column=0,columnspan=2)
        if plus_minus_btns:
            ttk.Button(self,text="+",command=lambda:self.set_value(self.val.get()+jump)).grid(row=2,column=2)
            ttk.Button(self,text="-",command=lambda:self.set_value(self.val.get()-jump)).grid(row=2,column=1)

    def get_value(self):
        return self.val.get()

    """
    Adds a listener that will be notified when value is changed
    """
    def add_listener(self, listener) -> None:
        self.listeners.append(listener)

    """
    Updates lables to show current values
    """
    def update_labels(self, as_click:bool=True) -> None:
        if self.max_val is not None and self.val.get() > self.max_val:
            self.val.set(self.max_val)
        elif self.min_val is not None and self.val.get() < self.min_val:
            self.val.set(self.min_val)
        if not self.apply_btn and as_click:
            self.notify_listeners()

    def notify_listeners(self):
        for listener in self.listeners:
            listener.update_value(self.name, self.get_value())

    def set_value(self, value, as_click:bool=True) -> None:
        if (self.max_val is None or value <= self.max_val) and (self.min_val is None or self.min_val <= value):
            self.val.set(value)
            self.update_labels(as_click)

    """
    Sets the min value to a new value and updates the current value as necessary
    """
    def set_min(self, new_min:Union[int,None], as_click:bool=True) -> None:
        self.min_val = new_min
        if self.min_val is not None and self.max_val is not None and self.min_val > self.max_val:
            self.max_val = self.min_val
        if self.min_val is not None and self.min_val > self.val.get():
            self.val.set(self.min_val)
            self.update_labels(as_click)

    """
    Sets the max value to a new value and updates the current value as necessary
    """
    def set_max(self, new_max:Union[int,None], as_click=True) -> None:
        self.max_val = new_max
        if self.min_val is not None and self.max_val is not None and self.max_val < self.min_val:
            self.min_val = self.max_val
        if self.max_val is not None and self.max_val < self.val.get():
            self.val.set(self.max_val)
            self.update_labels(as_click)

"""
Displays a label and a value
Value can be updated
"""
class LabeledValue(ttk.Frame):

    def __init__(self, frm:ttk.Frame, label:str, value="None"):
        super().__init__(frm, borderwidth=2, relief='groove')
        self.label = tk.StringVar()
        self.value = tk.StringVar()

        self.label.set(label)
        self.value.set(str(value))

        ttk.Label(self, textvariable=self.label,anchor='center').grid(row=0,column=0,sticky='news')
        ttk.Label(self, textvariable=self.value,relief='sunken',anchor='center').grid(row=1,column=0,sticky='news')

    def set_value(self, value):
        self.value.set(str(value))

class LabelGroup(ttk.Frame):

    def __init__(self, frm:ttk.Frame, name:str, labels:list[tuple[str,any]]):
        super().__init__(frm, borderwidth=2, relief='groove')

        ttk.Label(self, text=name).grid(row=0,column=0,columnspan=len(labels),sticky='news')

        c = 0
        self.labels = dict[str,LabeledValue]()
        for label,value in labels:
            self.labels[label] = LabeledValue(self, label, value)
            self.labels[label].grid(row=1,column=c,sticky='news')
            c += 1

    def set_value(self, label, value):
        self.labels[label].set_value(value)

"""
UI to select buttons
Like SingleSelector but different style/ use implications
 - implies fewer options, less need to sort
"""
class ButtonGroup(ttk.Frame):

    def __init__(self, frm:ttk.Frame, name:str, options:list[str]=None,selected:str=None):
        super().__init__(frm, borderwidth=2, relief='groove')

        self.name = name
        if options is None:
            self.options = list[str]()
        else:
            self.options = options
        self.selected = selected
        self.listeners = []
        self.buttons = dict[str,ttk.Button]()

        self.select_style=ttk.Style()
        self.select_style.map("Mod.TButton", background = [("active", "red"), ("!active", "blue")])#, foreground = [("active", "yellow"), ("!active", "green")])

        self.__display_buttons()

    def __display_buttons(self):
        c=0
        for option in self.options:
            def notify(o=option):
                self.value_update(o)
            style = 'TButton'
            if option == self.selected:
                style = 'Mod.TButton'
            self.buttons[option] = ttk.Button(self,text=option,command=notify,style=style)
            self.buttons[option].grid(row=0,column=c,sticky='news')
            c+=1

    def set_options(self, options:list[str], selected:str=None):
        for button in self.buttons.values():
            button.destroy()
        self.buttons.clear()
        self.options.clear()
        self.options.extend(options)
        self.selected = selected
        self.__display_buttons()

    def add_listener(self, listener):
        self.listeners.append(listener)

    def value_update(self, value:str):
        if self.selected is not None:
            self.buttons[self.selected].configure(style='TButton')
        self.selected = value
        self.buttons[self.selected].configure(style='Mod.TButton')

        for listener in self.listeners:
            listener.update_value(self.name, value)

    def set_highlight(self, value:str) -> bool:
        if value in self.buttons.keys():
            if self.selected is not None:
                self.buttons[self.selected].configure(style='TButton')
            self.selected = value
            self.buttons[self.selected].configure(style='Mod.TButton')
            return True
        return False

class LabeledEntry(ttk.Frame):

    def __init__(self, frm:ttk.Frame, label:str, apply_btn:bool=True,*,additional_buttons:dict[str,]=None):#TODO figure out how to type hint functions
        super().__init__(frm, borderwidth=2, relief='groove')

        self.label = label
        self.apply_btn = apply_btn
        self.entry = tk.StringVar()
        self.listeners = []

        r = 0
        ttk.Label(self,text=self.label).grid(row=r,column=0,sticky='news')
        ttk.Entry(self,textvariable=self.entry).grid(row=r+1,column=0,sticky='news')
        r += 2
        if self.apply_btn:
            ttk.Button(self,text='Apply',command=self.value_update).grid(row=r,column=0,sticky='news')
            r += 1
        if additional_buttons is not None:
            for name in additional_buttons:
                ttk.Button(self,text=name,command=additional_buttons[name]).grid(row=r,column=0,sticky='news')
                r += 1

    def get_entry(self) -> str:
        return self.entry.get()
    
    def set_entry(self, string):
        self.entry.set(string)

    def add_listenter(self, listener):
        self.listeners.append(listener)

    def value_update(self):
        for listener in self.listeners:
            listener.update_value(self.label, self.entry.get())

class MatchupView(ttk.Frame):

    def __init__(self, frm:ttk.Frame):
        super().__init__(frm, borderwidth=2, relief='groove')

        self.attached = False
        self.matchup = None

    def attach(self, matchup:foosballgame.FoosballMatchup) -> None:
        if not self.attached:
            self.attached = True
            self.matchup = matchup

            if self.matchup.is_over():
                self.home = LabeledValue(self,self.matchup.home_team,self.matchup.home_score)
                self.home.grid(row=1,column=0,sticky='news')
                self.away = LabeledValue(self,self.matchup.away_team,self.matchup.away_score)
                self.away.grid(row=0,column=0,sticky='news')
            else:
                self.home = ValueAdjustor(self,self.matchup.home_team,self.matchup.home_score,0,self.matchup.game_to)
                self.away = ValueAdjustor(self,self.matchup.away_team,self.matchup.away_score,0,self.matchup.game_to)

                self.home.add_listener(self)
                self.away.add_listener(self)

                self.home.grid(row=1,column=0,sticky='news')
                self.away.grid(row=0,column=0,sticky='news')

    def detach(self) -> None:
        self.attached = False
        self.matchup = None

        self.home.destroy()
        self.away.destroy()

    def update_value(self, name, value):
        self.matchup.set_score(name, value)
        if self.matchup.is_over():
            self.home.destroy()
            self.away.destroy()
            self.home = LabeledValue(self,self.matchup.home_team,self.matchup.home_score)
            self.home.grid(row=1,column=0,sticky='news')
            self.home = LabeledValue(self,self.matchup.away_team,self.matchup.away_score)
            self.home.grid(row=0,column=0,sticky='news')

class BracketView(ttk.Frame):

    def __init__(self, frm:ttk.Frame):
        super().__init__(frm)
        self.attached = False
        self.tournament = None
        self.views=list[MatchupView]()

    def attach(self, tournament:tournament.Tournament) -> None:
        if not self.attached:
            self.attached = True
            self.tournament = tournament

            for view in self.views:
                view.destroy()

            self.update()

    def update(self):
        c = 0
        for round in self.tournament.round_results:
            r = 0
            for group in round:
                for matchup in group.matchups:
                    new = MatchupView(self)
                    new.attach(matchup)
                    new.grid(row=r,column=c,sticky='news')
                    self.views.append(new)
                    r += 1
                    if r > 3:
                        r = 0
                        c += 1
            c += 1

    def detach(self) -> None:
        self.attached = False
        self.tournament = None

    def reset(self) -> None:
        pass

    def update_labels(self) -> None:
        pass

class PerformanceView(ttk.Frame):

    def __init__(self, frm:ttk.Frame, name:str, n_best:int=3, performances:list[records.Performance]=None):
        super().__init__(frm, borderwidth=2, relief='groove')
        
        ttk.Label(self,text=name).grid(row=0,column=0,columnspan=4,sticky='news')

        self.name = name
        self.n = n_best

        if performances is None:
            self.performances = list[records.Performance]()
        else:
            self.performances = performances

        self.num_lbls = list[ttk.Label]()
        self.other_lbls = list[ttk.Label]()
        self.update_labels()

    def set_n(self, n:int):
        if n >= 1:
            self.n = n
            self.clear_lbls()
            self.update_labels()

    def clear_lbls(self):
        for lbl in self.num_lbls:
            lbl.destroy()
        for lbl in self.other_lbls:
            lbl.destroy()
        self.num_lbls.clear()
        self.other_lbls.clear()

    def clear(self):
        self.performances.clear()
        self.clear_lbls()

    def update_labels(self):
        self.performances.sort(key=lambda x: x.result, reverse=True)
        place = 1
        tied = 0
        i = 0
        for performance in self.performances:
            if i > 0 and performance.result < self.performances[i-1].result:
                place += tied + 1
                tied = 0
                if place > self.n:
                    return
            elif i > 0 and performance.result == self.performances[i-1].result:
                tied += 1
            num = ttk.Label(self,text=place)#, borderwidth=2, relief='sunken')
            num.grid(row=i+1,column=0,sticky='news')
            self.num_lbls.append(num)

            name = ttk.Label(self,text=performance.player, borderwidth=2, relief='sunken')
            name.grid(row=i+1,column=1,sticky='news')
            self.other_lbls.append(name)

            result = ttk.Label(self,text=performance.result, borderwidth=2, relief='sunken')
            result.grid(row=i+1,column=2,sticky='news')
            self.other_lbls.append(result)

            #print(type(performance.on_date))
            if type(performance.on_date) == str:
                date_txt = performance.on_date
            elif performance.is_across_dates():
                from_date_txt = performance.on_date.strftime("%b %#d, %y")
                to_date_txt =   performance.to_date.strftime("%b %#d, %y")
                date_txt = f'{from_date_txt}-{to_date_txt}'
            elif performance.has_date():
                date_txt = performance.on_date.strftime("%b %#d, %y")
            elif performance.has_semester():
                date_txt = performance.semester
            else:
                date_txt = ''
            date = ttk.Label(self, text=date_txt, borderwidth=2, relief='sunken')
            date.grid(row=i+1,column=3,sticky='news')
            self.other_lbls.append(date)

            i += 1

    def add_performance(self, performance:records.Performance):
        self.performances.append(performance)
        self.clear_lbls()
        self.update_labels()

    def add_performances(self, performances:list[records.Performance]):
        self.performances.extend(performances)
        self.clear_lbls()
        self.update_labels()

    def set_performances(self, performances:list[records.Performance]):
        self.clear()
        self.add_performances(performances)

class PerformanceGroup(ttk.Frame):

    def __init__(self, frm:ttk.Frame, name:str, groups:list[tuple[str,list[records.Performance]]], n_best:int=3):
        super().__init__(frm, borderwidth=2, relief='groove')

        ttk.Label(self, text=name).grid(row=0,column=0,columnspan=len(groups),sticky='news')
        self.placed = False
        self.n = n_best
        c = 0
        self.performances = dict[str,PerformanceView]()
        for name,performances in groups:
            self.performances[name] = PerformanceView(self, name, self.n, performances)
            self.performances[name].grid(row=1,column=c,sticky='news')
            c += 1

    def set_performances(self, name:str, performances:records.Performance):
        self.performances[name].set_performances(performances)

    def set_n(self, n:int):
        if n >= 1:
            self.n = n
            for list in self.performances.values():
                list.set_n(n)

class ScrollFrame(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, borderwidth=2, relief='groove') # create a frame (self)

        self.canvas = tk.Canvas(self, borderwidth=0, background="#ffffff")          #place canvas on self
        self.viewPort = ttk.Frame(self.canvas)                                      #place a frame on the canvas, this frame will hold the child widgets 
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview) #place a scrollbar on self 
        self.canvas.configure(yscrollcommand=self.vsb.set)                          #attach scrollbar action to scroll of canvas

        self.vsb.pack(side="right", fill="y",expand=False)                                       #pack scrollbar to right of self
        self.canvas.pack(side="left", fill="both", expand=True)                     #pack canvas to left of self and expand to fil
        self.canvas_window = self.canvas.create_window((4,4), window=self.viewPort, anchor="nw",            #add view port frame to canvas
                                  tags="self.viewPort")

        self.viewPort.bind("<Configure>", self.onFrameConfigure)                       #bind an event whenever the size of the viewPort frame changes.
        self.canvas.bind("<Configure>", self.onCanvasConfigure)                       #bind an event whenever the size of the canvas frame changes.
            
        self.viewPort.bind('<Enter>', self.onEnter)                                 # bind wheel events when the cursor enters the control
        self.viewPort.bind('<Leave>', self.onLeave)                                 # unbind wheel events when the cursorl leaves the control

        self.onFrameConfigure(None)                                                 #perform an initial stretch on render, otherwise the scroll region has a tiny border until the first resize

    def onFrameConfigure(self, event):                                              
        '''Reset the scroll region to encompass the inner frame'''
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))                 #whenever the size of the frame changes, alter the scroll region respectively.

    def onCanvasConfigure(self, event):
        '''Reset the canvas window to encompass inner frame when required'''
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width = canvas_width)            #whenever the size of the canvas changes alter the window region respectively.

    def onMouseWheel(self, event):                                                  # cross platform scroll wheel event
        if platform.system() == 'Windows':
            self.canvas.yview_scroll(int(-1* (event.delta/120)), "units")
        elif platform.system() == 'Darwin':
            self.canvas.yview_scroll(int(-1 * event.delta), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll( -1, "units" )
            elif event.num == 5:
                self.canvas.yview_scroll( 1, "units" )
    
    def onEnter(self, event):                                                       # bind wheel events when the cursor enters the control
        if platform.system() == 'Linux':
            self.canvas.bind_all("<Button-4>", self.onMouseWheel)
            self.canvas.bind_all("<Button-5>", self.onMouseWheel)
        else:
            self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def onLeave(self, event):                                                       # unbind wheel events when the cursorl leaves the control
        if platform.system() == 'Linux':
            self.canvas.unbind_all("<Button-4>")
            self.canvas.unbind_all("<Button-5>")
        else:
            self.canvas.unbind_all("<MouseWheel>")