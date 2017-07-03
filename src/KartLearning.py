from sklearn import neural_network
from http.server import BaseHTTPRequestHandler, HTTPServer
import numpy as np
import pickle

from JoystickInput import getJoystickJson

#input a PIL.Image, return a numpy array containing it's data
def imageToNPArray(img):
    arr  = np.array(list(img.getdata()))
    s = arr.shape[0] * arr.shape[1]
    flat = arr.reshape(1, s)
    return flat[0]

def predictJoystickOutput(classifier, img):
    #TODO: implement this
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

#img -> 23 int list
file_name = 'samples/1/1'

with open(file_name, "rb") as input_file:
    raw_data = pickle.load(input_file)
    raw_data = raw_data[0:2]

data = [imageToNPArray(x[0]) for x in raw_data]
target = [x[1] for x in raw_data]

print('data[0] : ', data[0])
print('target[0] : ', target[0])

classifier = neural_network.MLPClassifier()
classifier.fit(data, target)

print('predict[0] : ', classifier.predict([data[0]]))
