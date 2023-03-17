from tkinter import *
from tkinter import ttk

class Screen(ttk.Frame):

    def __init__(self,root):
        super().__init__(root)
        self.views = {}
        self.view = None

    def add_view(self,name,view):
        self.views[name] = view

    def change_view(self,view):
        self.view = view
        self.__display()

    def __display(self):
        self.destroy()
        


    def destroy(self) -> None:
        super().destroy()