from http.server import BaseHTTPRequestHandler, HTTPServer
from JoystickInput import JoystickInput_SDL
from multiprocessing import Process
import sdl2 
import tkinter as tk

sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
globalJoystick = sdl2.SDL_JoystickOpen(0)
globalJoystickInput = JoystickInput_SDL(globalJoystick)

class myHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        sdl2.SDL_PumpEvents()
        output = globalJoystickInput.getJoystickJson()
        if(__name__ == '__main__'):
            print(output)

        self.wfile.write(str.encode(output))
        return

class JoystickServerFrame(object):
    def __init__(self, master):
        self.root = tk.Frame(master)

        self.startStopButtonText = tk.StringVar()
        self.startStopButtonText.set("Start Joystick Server")
        self.startStopButton = tk.Button(self.root, textvariable=self.startStopButtonText, command=self.startStopButtonClick)
        self.isRunning = False
        self.startStopButton.pack()

        self.root.pack()

    def startStopButtonClick(self):
        if(self.isRunning):
            self.startStopButtonText.set("Start Joystick Server")
            self.process.terminate()
        else:
            self.startStopButtonText.set("Stop Joystick Server")
            self.process = Process(target=runServer)
            self.process.start()

        self.isRunning = not self.isRunning

def runServer():
    try:
        PORT_NUMBER = 8082
        server = HTTPServer(('', PORT_NUMBER), myHandler)
        print('Started httpserver on port ' , PORT_NUMBER)
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()

if(__name__ == '__main__'):
    runServer()
