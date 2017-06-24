import sdl2, pygame, json

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

    def getJoystickJson(self, jState=None):
        if(jState == None):
            jState = self.getJoystickState()
        self.jDict = {}
        self.jDict['X_AXIS'] = jState[0]
        self.jDict['Y_AXIS'] = jState[1]
        self.jDict['START_BUTTON'] = jState[7]
        self.jDict['A_BUTTON'] = jState[18]
        self.jDict['B_BUTTON'] = jState[19]
        self.jDict['L_TRIG'] = jState[15]
        self.jDict['R_TRIG'] = jState[16]
        self.jDict['Z_TRIG'] = jState[14]
        return json.dumps(self.jDict)

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
