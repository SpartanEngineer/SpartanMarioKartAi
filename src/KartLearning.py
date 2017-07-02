from sklearn import neural_network
import numpy as np
import pickle

#input a PIL.Image, return a numpy array containing it's data
def imageToNPArray(img):
    arr  = np.array(list(img.getdata()))
    s = arr.shape[0] * arr.shape[1]
    flat = arr.reshape(1, s)
    return flat[0]

#img -> 23 int list
file_name = 'samples/1/1'

with open(file_name, "rb") as input_file:
    raw_data = pickle.load(input_file)

data = [imageToNPArray(x[0]) for x in raw_data]
target = [x[1] for x in raw_data]

print('data[0] : ', data[0])
print('target[0] : ', target[0])
