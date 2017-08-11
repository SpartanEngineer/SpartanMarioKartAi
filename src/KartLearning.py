from sklearn import neural_network
from http.server import BaseHTTPRequestHandler, HTTPServer
import numpy as np
import pickle, time, os, multiprocessing
import sdl2 

from JoystickInput import getJoystickJson, JoystickInput_SDL
from SpartanKartAi import getScreenShot, setGlobalWindowGeometry

#requires mupen64 and the input driver from:
#https://github.com/kevinhughes27/mupen64plus-input-bot

#input a PIL.Image, return a numpy array containing it's data
def imageToNPArray(img):
    arr  = np.array(list(img.getdata()))
    s = arr.shape[0] * arr.shape[1]
    flat = arr.reshape(1, s)
    return flat[0]

def predictJoystickOutput(classifier, img):
    if(classifier != None and img != None):
        prediction = classifier.predict([imageToNPArray(img)])[0]

        #convert np ints to regular python ints
        #result = [x.item() for x in prediction]

        #predicting just the X-axis for now
        result_actual = [0 for x in range(21)]
        result_actual[0] = prediction.item()
        result_actual[1] = 100
        result_actual[16] = 1
        return result_actual

    #if there's no classifier to use to predict, give it dummy output
    return [0 for x in range(21)]

class AIServerHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        sdl2.SDL_PumpEvents()
        joystick_state = globalJoystickInput.getJoystickState()
        global globalInputOverride, globalInProcessOfOverride

        if(joystick_state[12] == 1 and joystick_state[13] == 1 and not globalInProcessOfOverride):
            globalInputOverride = not globalInputOverride
            print('inputOverride:', globalInputOverride)
            globalInProcessOfOverride = True
        elif (globalInProcessOfOverride):
            globalInProcessOfOverride = (joystick_state[12] == 1 and joystick_state[13] == 1)

        if not globalInputOverride:
            #AI input
            if(not workerQueue.empty()):
                global globalOutputJson
                globalOutputJson = workerQueue.get()

            print(globalOutputJson)

            self.wfile.write(str.encode(globalOutputJson))

        else:
            #controller input
            output_json = getJoystickJson(joystick_state) 
            print(output_json)

            self.wfile.write(str.encode(output_json))

        return

def runAIServer(inputClassifierFile):
    try:
        global workerQueue, globalOutputJson, globalJoystickInput
        global globalInputOverride, globalInProcessOfOverride

        #init controller input
        sdl2.SDL_Init(sdl2.SDL_INIT_JOYSTICK)
        globalJoystick = sdl2.SDL_JoystickOpen(0)
        globalJoystickInput = JoystickInput_SDL(globalJoystick)
        globalInputOverride = True
        globalInProcessOfOverride = False

        setGlobalWindowGeometry('Mupen64Plus')

        with open(inputClassifierFile, 'rb') as input_file:
            classifier = pickle.load(input_file)

        globalOutputJson = getJoystickJson([0 for x in range(23)])

        workerQueue = multiprocessing.Queue(maxsize=1)
        workerThreadStopEvent = multiprocessing.Event()
        workerThread = multiprocessing.Process(target=aiServerWorkerThread, name='AI Server Worker Thread', args=(classifier, workerQueue, workerThreadStopEvent))
        workerThread.daemon = True

        PORT_NUMBER = 8082
        server = HTTPServer(('', PORT_NUMBER), AIServerHandler)
        workerThread.start()
        print('Started httpserver on port ' , PORT_NUMBER)
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()
        workerThreadStopEvent.set()

def aiServerWorkerThread(classifier, q, stop_event):
    while(not stop_event.is_set()):
        if q.empty():
            prediction = predictJoystickOutput(classifier, getScreenShot())
            prediction_json = getJoystickJson(prediction)
            q.put(prediction_json)

def trainClassifier(samplesDir, outputFileName):
    #TODO: finish implementing this
    startTime = time.time()
    classifier = neural_network.MLPClassifier()
    totalSamples = 0

    #process all the files in the directory
    for f in os.listdir(samplesDir):
        fileName = samplesDir + '/' + f

        try:
            with open(fileName, 'rb') as input_file:
                raw_data = pickle.load(input_file)

                data = [imageToNPArray(x[0]) for x in raw_data]

                #predicting just the X-axis for now
                target = [x[1][0] for x in raw_data]

                #print('data[0] : ', data[0])
                #print('target[0] : ', target[0])

                if(totalSamples == 0):
                    possible_classes = np.array([x for x in range(0, 201)])
                    classifier.partial_fit(data, target, classes=possible_classes)
                    #classifier.partial_fit(data, target)
                else:
                    classifier.partial_fit(data, target)

                totalSamples += len(data)

                print('processed file:', fileName)

        except Exception as e:
            print('Error:', e)
            print('Issue with file:', fileName)

    #save classifier to a file
    with open(outputFileName, 'wb') as output_file:
        pickle.dump(classifier, output_file)

    endTime = time.time() - startTime
    print('training took:', endTime)
    print('seconds per:', (endTime / len(data)))
    print('total samples:', totalSamples)

#trainClassifier('samples/1', 'nn_output2.pickle')
runAIServer('nn_output2.pickle')
