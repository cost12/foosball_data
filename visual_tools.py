import tkinter as tk
from tkinter import ttk
from typing import Union

import constants as c
import foosballgame
import tournament

""" TODO: should duplicates be allowed? right now they are
Select values from a list of values
"""
class MultiSelector(ttk.Frame):

    def __init__(self, frm:ttk.Frame, name:str, options:list[str] = None, apply_btn:bool=False, sorted:bool=True) -> None:
        super().__init__(frm, borderwidth=2, relief='groove')

        self.frm = frm
        self.name = name
        if options is None:
            self.options = list[str]()
        else:
            self.options = options
        self.apply_btn = apply_btn
        self.sorted = sorted

        self.listeners = []

        self.selected = list[tk.IntVar]()
        self.check_btns = list[ttk.Checkbutton]()

        ttk.Label(self,text=self.name).grid(row=0,column=0,columnspan=2,sticky='news')
        self.__place_buttons()

        ttk.Button(self, text='Select All',   command=self.select_all).grid(row=1,column=1,sticky='news')
        ttk.Button(self, text='Deselect All', command=self.deselect_all).grid(row=2,column=1,sticky='news')

        if apply_btn:
            ttk.Button(self, text='Apply', command=self.value_update).grid(row=3,column=1,sticky='news')

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
            if not self.apply_btn and like_click:
                self.value_update()
            return True
        return False

    def deselect(self, option:str, like_click:bool=True) -> bool:
        if option in self.options:
            if self.selected[self.options.index(option)]:
                self.check_btns[self.options.index(option)].state(['!selected'])
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

    def remove_option(self, option:str) -> bool:
        if option in self.options:
            index = self.options.index(option)
            btn = self.check_btns.pop(index)
            btn.destroy()
            self.options.pop(index)
            self.selected.pop(index)
            for i in range(index,len(self.check_btns)):
                btn.grid(row=i,column=0,sticky='news')
            return True
        return False
    
    def add_option(self, option:str, select:bool=True) -> None:
        if self.sorted:
            if c.DEBUG_MODE:
                print("Error: Multiselector.add_option not implemented for sorted selections")
        else:
            self.options.append(option)
            self.selected.append(tk.IntVar())
            self.selected[-1].set(1)
            if self.apply_btn:
                self.check_btns.append(ttk.Checkbutton(self, text=option, variable=self.selected[-1], onvalue=1, offvalue=0))
            else:
                self.check_btns.append(ttk.Checkbutton(self, text=option, variable=self.selected[-1], onvalue=1, offvalue=0, command=self.value_update))
            self.check_btns[-1].state(['!alternate'])
            if select:
                self.check_btns[-1].state(['selected'])
            self.check_btns[-1].grid(row=len(self.options),column=0,sticky='news')

    def add_options(self, options:list[str]) -> None:
        for option in options:
            self.add_option(option)

    def set_options(self, options:list[str]) -> None:
        self.clear_options()
        self.options.extend(options)
        self.__place_buttons()

    def __place_buttons(self):
        r=1
        if self.sorted:
            self.options.sort()
        for option in self.options:
            self.selected.append(tk.IntVar())
            self.selected[-1].set(1)
            if self.apply_btn:
                self.check_btns.append(ttk.Checkbutton(self, text=option, variable=self.selected[-1], onvalue=1, offvalue=0))
            else:
                self.check_btns.append(ttk.Checkbutton(self, text=option, variable=self.selected[-1], onvalue=1, offvalue=0, command=self.value_update))
            self.check_btns[-1].state(['!alternate'])
            self.check_btns[-1].state(['selected'])
            self.check_btns[-1].grid(row=r,column=0,sticky='news')
            r += 1

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

    def __init__(self, frm:ttk.Frame, name:str, low_val:int=0, high_val:int=10, min_val:Union[int,None]=None, max_val:Union[int,None]=None):
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
        self.min_adj = ValueAdjustor(self,'min',self.low_val,self.min_val,self.high_val)
        self.min_adj.grid(row=r,column=0,sticky='news')
        self.min_adj.add_listener(self)
        self.max_adj = ValueAdjustor(self,'max',self.high_val,self.low_val,self.max_val)
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
    
    def __init__(self, frm:ttk.Frame, name:str, cur_val:float=0, min_val:Union[float,None]=None, max_val:Union[float,None]=None, step:float=1) -> None:
        super().__init__(frm, borderwidth=2, relief='raised')

        assert ((min_val is not None and min_val <= cur_val) or min_val is None) and ((max_val is not None and cur_val <= max_val) or max_val is None)

        self.frm = frm
        self.name = name
        self.value = cur_val
        self.max_val = max_val
        self.min_val = min_val
        self.step = step

        self.listeners = []

        r = 0
        ttk.Label(self,text=self.name,anchor='c').grid(row=r,column=0,columnspan=3,sticky='news')
        r += 1
        ttk.Button(self,text='-',command=self.decrease).grid(row=r,column=0)#,sticky='news')
        self.val_lbl = ttk.Label(self,text=self.value,anchor='c')
        self.val_lbl.grid(row=r,column=1,sticky='news')
        ttk.Button(self,text='+',command=self.increase).grid(row=r,column=2)#,sticky='news')

    """
    Adds a listener that will be notified when value is changed
    """
    def add_listener(self, listener) -> None:
        self.listeners.append(listener)

    """
    Updates lables to show current values
    """
    def update_labels(self) -> None:
        text = self.value
        if type(self.value) == float:
            text = f'{self.value:.3f}'
        self.val_lbl.config(text=text)
        for listener in self.listeners:
            listener.update_value(self.name, self.value)

    """
    If it's within range, decreases the value and updates the label
    """
    def decrease(self) -> None:
        if self.min_val is None or self.value > self.min_val:
            self.value = max(self.value - self.step, self.min_val)
            self.update_labels()

    """
    If it's within range, increases the value and updates the label
    """
    def increase(self) -> None:
        if self.max_val is None:
            self.value = self.value + self.step
            self.update_labels()
        elif self.value < self.max_val:
            self.value = min(self.value + self.step, self.max_val)
            self.update_labels()

    def set_value(self, value) -> None:
        if (self.max_val is None or value <= self.max_val) and (self.min_val is None or self.min_val <= value):
            self.value = value
            self.update_labels()

    """
    Sets the min value to a new value and updates the current value as necessary
    """
    def set_min(self, new_min:Union[int,None]) -> None:
        self.min_val = new_min
        if self.min_val is not None and self.max_val is not None and self.min_val > self.max_val:
            self.max_val = self.min_val
        if self.min_val is not None and self.min_val > self.value:
            self.value = self.min_val
            self.update_labels()

    """
    Sets the max value to a new value and updates the current value as necessary
    """
    def set_max(self, new_max:Union[int,None]) -> None:
        self.max_val = new_max
        if self.min_val is not None and self.max_val is not None and self.max_val < self.min_val:
            self.min_val = self.max_val
        if self.max_val is not None and self.max_val < self.value:
            self.value = self.max_val
            self.update_labels()

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

    def attach(self, tournament:tournament.Tournament) -> None:
        if not self.attached:
            self.attached = True
            self.tournament = tournament

            self.update()

    def update(self):
        c = 0
        for round in self.tournament.round_results:
            r = 0
            for matchup in round.matchups:
                new = MatchupView(self)
                new.attach(matchup)
                new.grid(row=r,column=c,sticky='news')
                r += 1
            c += 1

    def detach(self) -> None:
        self.attached = False
        self.tournament = None

    def reset(self) -> None:
        pass

    def update_labels(self) -> None:
        pass