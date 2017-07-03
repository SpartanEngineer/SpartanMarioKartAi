import sdl2, pygame, json

SDL_AXIS_MAX = 32768
JSON_AXIS_MAX = 100
SDL_AXIS_CONVERT = SDL_AXIS_MAX / JSON_AXIS_MAX

def getJoystickJson(jState):
    jDict = {}
    jDict['X_AXIS'] = int(jState[0] / SDL_AXIS_CONVERT)
    jDict['Y_AXIS'] = -int(jState[1] / SDL_AXIS_CONVERT)
    jDict['START_BUTTON'] = jState[7]
    jDict['A_BUTTON'] = jState[18]
    jDict['B_BUTTON'] = jState[19]
    jDict['L_TRIG'] = jState[13]
    jDict['R_TRIG'] = jState[15]
    jDict['Z_TRIG'] = jState[14]
    return json.dumps(jDict)

#SDL input
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

#pygame input
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
