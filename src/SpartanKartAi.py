from mss import mss
from PIL import Image, ImageTk
from collections import deque
import tkinter as tk
import threading, queue, time, sys, pygame, sdl2, pickle

globalJoystick, globalJoystickInput = None, None

#window handling code, it has to be platform specific unfortunately
if sys.platform == 'linux':
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

elif sys.platform == 'win32' or sys.platform == 'cygwin':
    import win32gui

    def findWindowCallback(hwnd, name):
        theName = win32gui.GetWindowText(hwnd)
        if name in theName :
            global win32_rect
            win32_rect = win32gui.GetWindowRect(hwnd)

    def getWindowGeometry(name):
        global win32_rect
        win32_rect = (200, 200, 600, 400)
        win32gui.EnumWindows(findWindowCallback, name)
        x = win32_rect[0]
        y = win32_rect[1]
        w = win32_rect[2] - x
        h = win32_rect[3] - y
        return (x, y, w, h)

windowGeometry = getWindowGeometry('Mupen64Plus')
screenShotReSize = 320, 240

def getScreenShot():
    with mss() as sct:
        x = windowGeometry[0]
        y = windowGeometry[1]
        width = windowGeometry[2]
        height = windowGeometry[3]
        mon = {'top': y, 'left': x, 'width': width, 'height': height}

        img = Image.frombytes('RGB', (width, height), sct.get_pixels(mon))
        img.thumbnail(screenShotReSize, Image.ANTIALIAS)
        return img

class JoystickInput():

    def __init__(self, joystick):
        self.joystick = joystick

    def getJoystickState(self):
        self.joystick.init()
        self.result = []

        for i in range(self.joystick.get_numaxes()):
            self.axis = self.joystick.get_axis( i )
            self.result.append(self.axis)

        for i in range(self.joystick.get_numbuttons()):
            self.button = self.joystick.get_button(i)
            self.result.append(self.button)

        return self.result

    def getJoystickName(self):
        return self.joystick.get_name()

class JoystickInput_SDL():

    def __init__(self, joystick):
        self.joystick = joystick
        self.numAxes = min(sdl2.SDL_JoystickNumAxes(self.joystick), 4)
        self.numButtons = sdl2.SDL_JoystickNumButtons(self.joystick)

    def getJoystickState(self):
        self.result = []

        for i in range(self.numAxes):
            self.axis = sdl2.SDL_JoystickGetAxis(self.joystick, i) 
            self.result.append(self.axis)

        for i in range(self.numButtons):
            self.button = sdl2.SDL_JoystickGetButton(self.joystick, i)
            self.result.append(self.button)

        return self.result

    def getJoystickName(self):
        return sdl2.SDL_JoystickName(self.joystick)

def getJoystickState(joystickInput):
    return joystickInput.getJoystickState()

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
      sdl2.SDL_PumpEvents()
      q.put((getScreenShot(), getJoystickState(globalJoystickInput)))

class App(object):

  def __init__(self):
    self.root = tk.Tk()

    self.fpsCounter = FPSCounter()
    self.fpsLabel = tk.Label(text='')
    self.fpsLabel.pack()

    self.ss = getScreenShot()
    self.ssLabel = tk.Label(image=ImageTk.PhotoImage(self.ss))
    self.ssLabel.pack()

    self.isRecording = False
    self.recordFrame = tk.Frame(self.root)

    self.recordLabel = tk.Label(self.recordFrame, text='Output Location: ')
    self.recordLabel.pack(side=tk.LEFT)

    self.recordEntry = tk.Entry(self.recordFrame)
    self.recordEntry.pack(side=tk.LEFT)

    self.recordButtonText = tk.StringVar()
    self.recordButtonText.set("Start Recording")
    self.recordButton = tk.Button(self.recordFrame, textvariable=self.recordButtonText, command=self.recordButtonClick)
    self.recordButton.pack(side=tk.LEFT)

    self.recordTimeRunningText = tk.StringVar()
    self.recordTimeRunningText.set('0')
    self.recordTimeRunningLabel = tk.Label(self.recordFrame, textvariable=self.recordTimeRunningText)
    self.recordTimeRunningLabel.pack(side=tk.LEFT)

    self.recordFrame.pack()

    self.jsTextArea = tk.Text(height=3)
    self.jsTextArea.pack()

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

      self.ss = ImageTk.PhotoImage(self.queue_head[0])
      self.ssLabel.configure(image=self.ss)
      self.ssLabel.update_idletasks()

      self.jsString = str(self.queue_head[1])
      self.jsTextArea.delete(1.0, tk.END)
      self.jsTextArea.insert(1.0, self.jsString)

      if(self.isRecording):
          self.recordData.append(self.queue_head)
          self.recordTimeRunningText.set("%.2f" % (time.time()-self.recordTimeStarted))

    self._poll_job_id = self.root.after(self.poll_interval, self.poll)

  def recordButtonClick(self):
    self.isRecording = not self.isRecording
    if(self.isRecording):
      self.recordTimeStarted = time.time()
      self.recordData = []
      self.recordButtonText.set("Stop Recording")
    else:
      self.recordButtonText.set("Start Recording")
      with open('output_test.pickle', 'wb') as self.handle:
          pickle.dump(self.recordData, self.handle)

pygame.init()
pygame.joystick.init()
sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
globalJoystick = sdl2.SDL_JoystickOpen(0)
globalJoystickInput = JoystickInput_SDL(globalJoystick)
app = App()
app.root.mainloop() 
pygame.quit()
sdl2.SDL_Quit()
