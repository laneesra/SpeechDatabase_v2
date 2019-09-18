from .db import select_speaker_features, init_db
from keras.models import load_model, Model
import numpy as np
from scipy.spatial import KDTree
from sklearn.preprocessing import normalize
from pydub import AudioSegment
import io
import os
from scipy import signal
from sklearn.preprocessing import StandardScaler
from keras.utils import CustomObjectScope
from keras.layers import Conv2D, ZeroPadding2D, Activation, Input, concatenate, Dropout, Subtract, BatchNormalization, Dot
from keras.layers.pooling import MaxPooling2D
from keras.models import Model
from keras.regularizers import l2
from keras.layers.core import Lambda, Flatten, Dense
from keras.models import Sequential
FRAME_RATE = 16000
CHANNELS = 1
MS = 1.0/FRAME_RATE
NPERSEG = int(0.025/MS)
NOVERLAP = int(0.015/MS)
NFFT = 512
SIZE_FFT = NFFT//2
WINDOW = FRAME_RATE*1
BATCH_SIZE = 32
SIZE_COLS = int(np.ceil((WINDOW - NPERSEG)/(NPERSEG - NOVERLAP)))
ANGLE_THRESHOLD = 0.8
THRESHOLD = (2 - 2 * np.cos(ANGLE_THRESHOLD)) ** 0.5 # 0.013962521


class WeightsInitializer:
    def __call__(self, shape, name=None):
        return initialize_weights(shape, name=name)


class BiasInitializer:
    def __call__(self, shape, name=None):
        return initialize_bias(shape, name=name)


def initialize_weights(shape, name=None):
    return np.random.normal(loc=0.0, scale=1e-2, size=shape)


def initialize_bias(shape, name=None):
    return np.random.normal(loc=0.5, scale=1e-2, size=shape)


class SpeakerRecognition:
    def __init__(self, model_path, conf, output):
        self.encoder = self.init_model(model_path)
        self.db = init_db(conf)
        fc = select_speaker_features(self.db)
        self.feature_centers = {f[0]: normalize(np.array(f[1]).reshape(1, -1))[0] for f in fc}
        self.tree = KDTree(list(self.feature_centers.values()))
        self.output = output

    def init_model(self, model_path):
        with CustomObjectScope({'initialize_weights': WeightsInitializer, 'initialize_bias': BiasInitializer}):
            input_shape = (SIZE_FFT, SIZE_COLS, 3)
            model = Sequential()
            model.add(Conv2D(64, (10, 10), activation='relu', input_shape=input_shape,
                             kernel_initializer=initialize_weights, kernel_regularizer=l2(2e-4)))
            model.add(BatchNormalization())
            model.add(MaxPooling2D())

            model.add(Conv2D(128, (7, 7), activation='relu',
                             kernel_initializer=initialize_weights,
                             bias_initializer=initialize_bias, kernel_regularizer=l2(2e-4)))
            model.add(BatchNormalization())
            model.add(MaxPooling2D())

            model.add(Conv2D(128, (4, 4), activation='relu', kernel_initializer=initialize_weights,
                             bias_initializer=initialize_bias, kernel_regularizer=l2(2e-4)))
            model.add(BatchNormalization())
            model.add(MaxPooling2D())

            model.add(Conv2D(256, (4, 4), activation='relu', kernel_initializer=initialize_weights,
                             bias_initializer=initialize_bias, kernel_regularizer=l2(2e-4)))
            model.add(Flatten())
            model.add(Dense(1024, activation='softmax',
                            kernel_regularizer=l2(1e-3),
                            kernel_initializer=initialize_weights, bias_initializer=initialize_bias))
            model.load_weights(model_path)
            return model

    def read_bytes(self, raw_data, filename):
        wav = io.BytesIO(raw_data)
        wav = AudioSegment.from_raw(wav, channels=1, frame_rate=44100, sample_width=2)
        if filename.split('.')[-1] not in ['wav']:
            filename += '.wav'
        filename = os.path.join(self.output, filename) #todo from conf
        wav.export(filename, format='wav')
        sound = AudioSegment.from_file(filename, format="wav")
        samples = sound.get_array_of_samples()
        return samples

    def get_voice_units(self, raw_data, filename):
        samples = self.read_bytes(raw_data, filename)
        units = []
        for i in range(samples // WINDOW):
            if WINDOW * (i + 1) <= len(samples):
                s = samples[WINDOW * i:WINDOW * (i + 1)]
                f, t, Sxx = signal.spectrogram(s, FRAME_RATE, window='hamming', nperseg=NPERSEG,
                                               noverlap=NOVERLAP,
                                               nfft=NFFT, detrend='constant', return_onesided=False, scaling='density',
                                               axis=-1)
                Hxx = StandardScaler().fit_transform(Sxx)
                u = {'spectr': Hxx[0:SIZE_FFT, :].reshape(SIZE_FFT, SIZE_COLS, 1), 'start': WINDOW * i, 'end': WINDOW * (i + 1)}
                units.append(u)
        return units

    def get_feature_vector(self, voice_units):
        features = self.encoder.predict([voice_units])
        for i, f in enumerate(features):
            voice_units[i]['feature_vector'] = f
        return np.mean(features)

    def get_kd_tree_nearest(self, point):
        """
        find the nearest cluster
        """
        #todo find with postgres
        return self.tree.query(point, 1)

    def detect_voice(self, raw_data, filename):
        voice_units = self.get_voice_units(raw_data, filename) #dict
        feature_vector = self.get_feature_vector(voice_units)
        dist, closest_arg = self.get_kd_tree_nearest(normalize(np.array(feature_vector).reshape(1, -1))[0])
        if dist > THRESHOLD:
            print('there is no samples of such face, adding new person to db')
            return None, feature_vector
        else:
            closest_id = list(self.feature_centers.keys())[closest_arg]
            return closest_id, feature_vector

