import tkinter as tk
from tkinter import ttk
import os, pickle

samples_dir = 'samples'

class DataViewerApp(object):

  def __init__(self):
    self.root = tk.Tk()
    self.root.wm_title("SpartanMarioKartAi - View Training Data")

    self.treeFrame = tk.Frame(self.root)
    self.treeYScroll = tk.Scrollbar(self.treeFrame, orient=tk.VERTICAL)
    self.treeYScroll.pack(side=tk.RIGHT, fill=tk.Y)
    self.tree = ttk.Treeview(self.treeFrame, yscrollcommand=self.treeYScroll.set)
    self.tree["columns"] = ("one")
    self.tree.column("one", width=100)
    self.tree.heading("one", text="is directory?")
    self.tree.bind("<<TreeviewSelect>>", self.loadListBox)
    self.treeYScroll.config(command=self.tree.yview)
    self.loadTree(samples_dir)
    self.tree.pack()
    self.treeFrame.pack()

    self.listboxFrame = tk.Frame(self.root)
    self.listboxYScroll = tk.Scrollbar(self.listboxFrame, orient=tk.VERTICAL)
    self.listboxYScroll.pack(side=tk.RIGHT, fill=tk.Y)
    self.listbox = tk.Listbox(self.listboxFrame, yscrollcommand=self.listboxYScroll.set)
    self.listboxYScroll.config(command=self.listbox.yview)
    self.listbox.pack()
    self.listboxFrame.pack()

  #load the file system into the treeview
  def loadTree(self, rootDir):
      self.tree.delete(*self.tree.get_children())
      self.tree.insert('', tk.END, rootDir, text=rootDir, values=("yes"))
      self.loadTreeRecursive(rootDir)

  def loadTreeRecursive(self, rootDir):
      for f in os.listdir(rootDir):
          fullName = rootDir + '/' + f
          isDir = os.path.isdir(fullName)
          if(isDir):
              dirValue = "yes"
          else:
              dirValue = "no"
          self.tree.insert(rootDir, tk.END, fullName, text=f, values=(dirValue))
          if(isDir):
              self.loadTreeRecursive(fullName)

  def loadListBox(self, event):
      self.listbox.delete(0, tk.END)
      selected_item = self.tree.focus()
      try:
          if(not os.path.isdir(selected_item)):
            with open(selected_item, "rb") as input_file:
                self.sampleData = pickle.load(input_file)
                for i in range(len(self.sampleData)):
                    self.listbox.insert(tk.END, str(i))
      except:
          print('error loading selected file: ' + selected_item)

dataViewer = DataViewerApp()
dataViewer.root.mainloop()
