import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os, pickle

samples_dir = 'samples'

class DataViewerFrame(object):

  def __init__(self, master):
    self.root = tk.Frame(master)

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
    self.listbox.bind("<<ListboxSelect>>", self.loadScreenshotIntoLabel)
    self.listboxYScroll.config(command=self.listbox.yview)
    self.listbox.pack()
    self.listboxFrame.pack()

    self.ssLabel = tk.Label(self.root)
    self.ssLabel.pack()

    self.root.pack()

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
                self.sampleDataDict = {}
                for i in range(len(self.sampleData)):
                    self.listbox.insert(tk.END, str(i))
                    self.sampleDataDict[str(i)] = self.sampleData[i]

      except Exception as e:
        print('error loading selected file: ' + selected_item)
        print(str(e))

  def loadScreenshotIntoLabel(self, event):
      selected_item = self.listbox.curselection()
      selected_index = int(selected_item[0])
      self.ss = ImageTk.PhotoImage(self.sampleData[selected_index][0])
      self.ssLabel.configure(image=self.ss)
      self.ssLabel.update_idletasks()

root = tk.Tk()
root.wm_title("SpartanMarioKartAi - View Training Data")
dataViewer = DataViewerFrame(root)
root.mainloop()
