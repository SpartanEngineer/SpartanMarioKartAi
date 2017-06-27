import tkinter as tk
from tkinter import ttk

samples_dir = 'samples'

class DataViewerApp(object):

  def __init__(self):
    self.root = tk.Tk()
    self.root.wm_title("SpartanMarioKartAi - View Training Data")

    self.tree = ttk.Treeview(self.root)

    self.tree.insert('', 'end', "Item1", text="Item1")
    self.tree.insert('', 'end', "Item2", text="Item2")
    self.tree.insert('', 'end', "Item3", text="Item3")

    self.tree.insert("Item1", 'end', "SubItem1", text="SubItem1")
    self.tree.insert("Item1", 'end', "SubItem2", text="SubItem2")

    self.tree.pack()

dataViewer = DataViewerApp()
dataViewer.root.mainloop()
