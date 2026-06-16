import os
import numpy as np
from scipy.signal import resample
import xml.etree.ElementTree as ET
from sklearn.preprocessing import StandardScaler
import keras


class Recognizer:
    def __init__(self):
        self.gestures = ['circle', 'delete_mark', 'rectangle']
        self.NUM_POINTS = 64
        self.model = keras.models.load_model("gesture_recognizer.keras")
        self.scaler = StandardScaler()

    def preprocess_data(self, points):
        points = np.array(points, dtype=float)
        points = self.scaler.scale(points)

        resampled = resample(points, self.NUM_POINTS)
        return resampled

    def recognize(self, points):
        scaled = self.scaler.fit_transform(points)
        resampled = resample(scaled, self.NUM_POINTS)
        resampled = np.expand_dims(resampled, axis=0) #add dimension
        prediction = self.model.predict(resampled, verbose=0)
        index = np.argmax(prediction[0])
        self.predicted_gesture = self.gestures[index]
        # print("Predicted gesture: ", self.predicted_gesture)
        return self.predicted_gesture
