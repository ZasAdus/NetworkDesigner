import tkinter as tk
from tkinter import ttk
from router import Router
from switch import Switch
from computer import Computer
from database import Database

class Interface:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Simulator")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        self.canvas = tk.Canvas(self.root, bg="white", width=800, height=600)
        self.canvas.pack()
        #Ahh shit here we go



def __main__():
    root = tk.Tk()
    app = Interface(root)
    root.mainloop()