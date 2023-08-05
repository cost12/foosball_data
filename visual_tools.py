import tkinter as tk
from tkinter import ttk
from typing import Union

""" TODO: should duplicates be allowed? right now they are
Select values from a list of values
"""
class MultiSelector(ttk.Frame):

    def __init__(self, frm:ttk.Frame, name:str, options:list[str] = None, apply_btn = False) -> None:
        super().__init__(frm, borderwidth=2, relief='groove')

        self.frm = frm
        self.name = name
        if options is None:
            self.options = list[str]()
        else:
            self.options = options
        self.apply_btn = apply_btn

        self.listeners = []

        self.selected = list[tk.IntVar]()
        self.check_btns = list[ttk.Checkbutton]()

        r = 0
        ttk.Label(self,text=self.name).grid(row=r,column=0,columnspan=2,sticky='news')
        r += 1
        for option in self.options:
            self.selected.append(tk.IntVar())
            self.selected[-1].set(1)
            if apply_btn:
                self.check_btns.append(ttk.Checkbutton(self, text=option, variable=self.selected[-1], onvalue=1, offvalue=0))
            else:
                self.check_btns.append(ttk.Checkbutton(self, text=option, variable=self.selected[-1], onvalue=1, offvalue=0, command=self.value_update))
            self.check_btns[-1].state(['!alternate'])
            self.check_btns[-1].state(['selected'])
            self.check_btns[-1].grid(row=r,column=0,sticky='news')
            r += 1

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
    def select_all(self) -> None:
        for btn,sel in zip(self.check_btns,self.selected):
            btn.state(['selected'])
            sel.set(1)
        if not self.apply_btn:
            self.value_update()

    """
    Deselects all values
    """
    def deselect_all(self) -> None:
        for btn,sel in zip(self.check_btns,self.selected):
            btn.state(['!selected'])
            sel.set(0)
        if not self.apply_btn:
            self.value_update()

    """
    Adds a listener that will be updated everytime different values are selected
    Listeners use update_value(name, value) to listen
    """
    def add_listener(self, listener) -> None:
        self.listeners.append(listener)

    def select(self, option:str) -> bool:
        if option in self.options:
            self.check_btns[self.options.index(option)].state(['selected'])
            if not self.apply_btn:
                self.value_update()
            return True
        return False

    def deselect(self, option:str) -> bool:
        if option in self.options:
            if self.selected[self.options.index(option)]:
                self.check_btns[self.options.index(option)].state(['!selected'])
            if not self.apply_btn:
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
    
    def add_option(self, option:str) -> None:
        self.options.append(option)
        self.selected.append(tk.IntVar())
        self.selected[-1].set(1)
        if self.apply_btn:
            self.check_btns.append(ttk.Checkbutton(self, text=option, variable=self.selected[-1], onvalue=1, offvalue=0))
        else:
            self.check_btns.append(ttk.Checkbutton(self, text=option, variable=self.selected[-1], onvalue=1, offvalue=0, command=self.value_update))
        self.check_btns[-1].state(['!alternate'])
        self.check_btns[-1].state(['selected'])
        self.check_btns[-1].grid(row=len(self.options),column=0,sticky='news')

    def add_options(self, options:list[str]) -> None:
        for option in options:
            self.add_option(option)

    def set_options(self, options:list[str]) -> None:
        self.clear_options()
        self.add_options(options)

""" TODO: should duplicates be allowed? right now they are
Select a value from a list of values
"""
class SingleSelector(ttk.Frame):

    def __init__(self, frm:ttk.Frame, name:str, options:list, apply_btn:bool=False) -> None:
        super().__init__(frm, borderwidth=2, relief='groove')

        self.frm = frm
        self.name = name
        self.options = options
        self.apply_btn = apply_btn

        self.listeners = []

        self.selected = tk.StringVar()
        self.btns = list[ttk.Radiobutton]()

        r = 0
        ttk.Label(self,text=self.name).grid(row=r,column=0,columnspan=2,sticky='news')
        r += 1
        for option in self.options:
            if apply_btn:
                self.btns.append(ttk.Radiobutton(self, text=option, variable=self.selected, value=option))
            else:
                self.btns.append(ttk.Radiobutton(self, text=option, variable=self.selected, value=option, command=self.value_update))
            self.btns[-1].grid(row=r,column=0,sticky='news')
            r += 1
        self.selected.set(self.options[0])

        if apply_btn:
            ttk.Button(self, text='Apply', command=self.value_update).grid(row=r,column=0,columnspan=2,sticky='news')

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


    def select(self, option:str) -> bool:
        if option in self.options:
            self.btns[self.options.index(option)].invoke()
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
                    self.btns[0].invoke()
                else:
                    self.selected.set('')
            return True
        return False
    
    def add_option(self, option:str) -> None:
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
        self.add_options(options)

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
        if self.max_val is None or self.value < self.max_val:
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