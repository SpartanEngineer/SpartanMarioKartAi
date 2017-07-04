from sklearn import neural_network
from http.server import BaseHTTPRequestHandler, HTTPServer
import numpy as np
import pickle, time, os

from JoystickInput import getJoystickJson

#input a PIL.Image, return a numpy array containing it's data
def imageToNPArray(img):
    arr  = np.array(list(img.getdata()))
    s = arr.shape[0] * arr.shape[1]
    flat = arr.reshape(1, s)
    return flat[0]

def predictJoystickOutput(classifier, img):
    #TODO: implement this
    #print('predict[0] : ', classifier.predict([data[0]]))
    return [0 for x in range(23)]

class AIServer(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        #TODO: finish this implementation
        output = predictJoystickOutput(None, None)
        output_json = getJoystickJson(output)

        print(output_json)

        self.wfile.write(str.encode(output_json))
        return

def trainClassifier(samplesDir, outputFileName):
    #TODO: finish implementing this
    startTime = time.time()
    classifier = neural_network.MLPClassifier()
    totalSamples = 0

    #process all the files in the directory
    for f in os.listdir(samplesDir):
        if(f != '1'):
            continue
        fileName = samplesDir + '/' + f

        with open(fileName, 'rb') as input_file:
            raw_data = pickle.load(input_file)
            #raw_data = raw_data[0:2]

            data = [imageToNPArray(x[0]) for x in raw_data]
            target = [x[1] for x in raw_data]

            print('data[0] : ', data[0])
            print('target[0] : ', target[0])

            classifier.fit(data, target)
            totalSamples += len(data)

        break

    #save classifier to a file
    with open(outputFileName, 'wb') as output_file:
        pickle.dump(classifier, output_file)

    endTime = time.time() - startTime
    print('training took: ', endTime)
    print('seconds per: ', (endTime / len(data)))

#print('predict[0] : ', classifier.predict([data[0]]))
trainClassifier('samples/1', 'nn_output.pickle')
