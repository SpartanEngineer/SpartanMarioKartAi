from http.server import BaseHTTPRequestHandler, HTTPServer
from JoystickInput import JoystickInput_SDL
import sdl2 

PORT_NUMBER = 8082
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
        print(output)

        self.wfile.write(str.encode(output))
        return

try:
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print('Started httpserver on port ' , PORT_NUMBER)
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
