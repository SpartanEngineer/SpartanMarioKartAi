from mss import mss
from PIL import Image, ImageTk
from collections import deque
import tkinter as tk
import threading, queue, time

#get window size/position using wnck (linux only)
import gi
gi.require_version('Wnck', '3.0')
from gi.repository import Wnck

def getWindowGeometry(name):
    Wnck.Screen.get_default().force_update()
    window_list = Wnck.Screen.get_default().get_windows()
    for win in window_list:
        if name in win.get_name():
            geometry = list(win.get_geometry())
            geometry[1] = geometry[1] + 25
            geometry[3] = geometry[3] - 25
            return geometry

    return (200, 200, 600, 400)

windowGeometry = getWindowGeometry('Mupen64Plus')

def getScreenShot():
    with mss() as sct:
        x = windowGeometry[0]
        y = windowGeometry[1]
        width = windowGeometry[2]
        height = windowGeometry[3]
        mon = {'top': y, 'left': x, 'width': width, 'height': height}

        img = Image.frombytes('RGB', (width, height), sct.get_pixels(mon))
        return ImageTk.PhotoImage(img)

class FPSCounter():

    def __init__(self):
        self.deque = deque(maxlen=60)

    def increment(self):
        self.deque.append(time.time())

    def getFPS(self):
        if(len(self.deque) <= 1):
            return 0

        self.elapsedTime = time.time() - self.deque[0]
        if(self.elapsedTime <= 0):
            return 0

        return len(self.deque) / self.elapsedTime

def ss_thread(q, stop_event):
  """q is a Queue object, stop_event is an Event.
  stop_event from http://stackoverflow.com/questions/6524459/stopping-a-thread-python
  """
  while(not stop_event.is_set()):
    if q.empty():
      q.put(getScreenShot())

class App(object):

  def __init__(self):
    self.root = tk.Tk()

    self.fpsCounter = FPSCounter()
    self.fpsLabel = tk.Label(text='')
    self.fpsLabel.pack()

    self.ss = getScreenShot()
    self.ssLabel = tk.Label(image=self.ss)
    self.ssLabel.pack()

    self.queue = queue.Queue(maxsize=1)
    self.poll_thread_stop_event = threading.Event()
    self.poll_thread = threading.Thread(target=ss_thread, name='Thread', args=(self.queue,self.poll_thread_stop_event))
    self.poll_thread.start()

    self.poll_interval = 10
    self.poll()

    self.root.wm_protocol("WM_DELETE_WINDOW", self.cleanup_on_exit)

  def cleanup_on_exit(self):
    """Needed to shutdown the polling thread."""
    self.poll_thread_stop_event.set()
    self.root.quit() #Allow the rest of the quit process to continue

  def poll(self):
    if self.queue.qsize():
      self.queue_head = self.queue.get()

      self.fpsCounter.increment()
      self.fpsText = "FPS: %.2f" % (self.fpsCounter.getFPS())
      self.fpsLabel.configure(text=self.fpsText)

      self.ss = self.queue_head
      self.ssLabel.configure(image=self.ss)
      self.ssLabel.update_idletasks()

    self._poll_job_id = self.root.after(self.poll_interval, self.poll)

app = App()
app.root.mainloop() 