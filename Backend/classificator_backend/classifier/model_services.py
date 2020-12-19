import tensorflow as tf
from django.conf import settings
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, Conv1D, GlobalMaxPooling1D
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import pickle
import re
import os
from tensorflow.python.client import device_lib

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

print(device_lib.list_local_devices())

config = tf.compat.v1.ConfigProto()
config.gpu_options.allow_growth = True
session = tf.compat.v1.Session(config=config)
tf.compat.v1.keras.backend.set_session(session)

class ClassificationPredictor:
    """Класс классификатора"""

    def __init__(self):
        self.numWords = 30000
        self.maxTextLen = 30
        self.modelCnnSavePath = settings.PATH_TO_MODEL
        self.tokenizatorPath = settings.PATH_TO_TOKENIZATOR

        self.model = Sequential()
        self.model.add(Embedding(self.numWords, 32, input_length=self.maxTextLen))
        self.model.add(Conv1D(250, 5, padding='valid', activation='relu'))
        self.model.add(GlobalMaxPooling1D())
        self.model.add(Dense(1128, activation='relu'))
        self.model.add(Dense(9, activation='softmax'))

        self.model.compile(optimizer='adam',
                          loss='categorical_crossentropy',
                          metrics=['accuracy'])

        self.model.load_weights(self.modelCnnSavePath)
        with open(self.tokenizatorPath, 'rb') as handle:
            self.tokenizer = pickle.load(handle)

    def getTextClass(self, text):
        """Возвращает int результат классификации для передаваемого текста"""
        textList = []
        text = self.delPunctuationAndInsig(text)
        textList.append(text)
        inputSequence = self.tokenizer.texts_to_sequences(textList)
        prepSequence = pad_sequences(inputSequence, maxlen=self.maxTextLen)
        prediction = self.model.predict(prepSequence)
        return np.argmax(prediction) + 1

    def delPunctuationAndInsig(self, string):
        """Обабатывает входной текст - удаляет незначимые символы и слова"""
        string = re.sub(r'[^\w\s]+|[\d]+|км/ч|\b\w{0,2}\b', r' ', string)
        string = re.sub(r'\b\w{0,2}\b', r'', string)
        string = re.sub(r'\b\s+\b', r' ', string.strip())
        return string.lower()


