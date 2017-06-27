import tkinter as tk
from tkinter import ttk
import os

samples_dir = 'samples'

class DataViewerApp(object):

  def __init__(self):
    self.root = tk.Tk()
    self.root.wm_title("SpartanMarioKartAi - View Training Data")

    self.tree = ttk.Treeview(self.root)
    self.loadTree(samples_dir)
    self.tree.pack()

  #load the file system into the treeview
  def loadTree(self, rootDir):
      self.tree.delete(*self.tree.get_children())
      self.tree.insert('', 'end', rootDir, text=rootDir)
      self.loadTreeRecursive(rootDir)

  def loadTreeRecursive(self, rootDir):
      for f in os.listdir(rootDir):
          self.tree.insert(rootDir, 'end', rootDir + '/' + f, text=f)
          if(os.path.isdir(rootDir + '/' + f)):
              self.loadTreeRecursive(rootDir + '/' + f)

dataViewer = DataViewerApp()
dataViewer.root.mainloop()
