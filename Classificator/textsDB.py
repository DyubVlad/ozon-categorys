import sqlite3
from xml.dom import minidom
import traceback
import sys
import os
import re
from collections import namedtuple
import bs4
import lxml

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, MaxPooling1D, Conv1D, GlobalMaxPooling1D, Dropout, LSTM, GRU
from tensorflow.keras import utils
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras import utils
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class TextsData:
    def __init__(self):
        try:
            self.conn = sqlite3.connect('textsFromOzon.db')
            self.cur = self.conn.cursor()
        except Exception as e:
            print('Error:: ' + str(e))
            traceback.print_exc(file=sys.stdout)
        self.createTabels()
        self.classInsert()
        self.statTexts = namedtuple('statTexts', 'classCat, countTexts')

    def createTabels(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS goods(
        itemId INTEGER PRIMARY KEY AUTOINCREMENT, 
        itemTitle TEXT, 
        itemDescription TEXT, 
        categoryId INTEGER );
        """)
        self.cur.execute("""CREATE TABLE IF NOT EXISTS categoryList(
        categoryId INTEGER PRIMARY KEY AUTOINCREMENT, 
        categoryName TEXT); 
        """)
        self.conn.commit()

    def classInsert(self):
        filePath = 'classes.txt'
        sqlTemplate = """INSERT INTO categoryList (categoryName)
        VALUES ('{category}')
        """
        f = open(filePath, encoding='utf-8')
        for line in f:
            if not self.checkClass(line.strip()):
                sqlMess = sqlTemplate.format(category=line.strip())
                self.cur.execute(sqlMess)
        self.conn.commit()

    def checkClass(self, className):
        sqlCheckTemp = """SELECT * FROM categoryList WHERE categoryName = '{category}'"""
        sqlCheckMess = sqlCheckTemp.format(category=className)
        if len(self.cur.execute(sqlCheckMess).fetchall()) == 0:
            return False
        else:
            return True

    def goodsInsert(self, title, description, category):
        sqlTemplate = """INSERT INTO goods (itemTitle, itemDescription, categoryid) 
        VALUES (
        '{itemTitle}', 
        '{itemDescription}',
        (SELECT categoryid FROM categoryList WHERE categoryName = '{categoryName}'))
        """
        sqlMess = sqlTemplate.format(itemTitle=title, itemDescription=description, categoryName=category)
        #print(title[:40] + '\n' + description[:40] + '\n' + category + '\n')
        try:
            self.cur.execute(sqlMess)
        except Exception as e:
            print(sqlMess + '\n')
            print('Error:: ' + str(e))
            traceback.print_exc(file=sys.stdout)
        self.conn.commit()

    def statistics(self):
        sqlMessCategory = """SELECT categoryid FROM categoryList"""
        sqlMessCount = """SELECT COUNT(*) FROM goods
        WHERE goods.categoryId = '{catId}'"""
        cats = self.cur.execute(sqlMessCategory).fetchall()
        classCount =[]
        for cat in cats:
            count = self.cur.execute(sqlMessCount.format(catId=str(cat[0]))).fetchone()
            classCount.append(self.statTexts(classCat=str(cat[0]), countTexts=str(count[0])))
            #print('CategoryId: ' + str(cat[0]) + ' textsCount: ' + str(count[0]))
        return classCount


class XmlParser:
    def __init__(self):
        self.tagValues = namedtuple('tagValues', 'title, description, category')

    def readXml(self, filePath):
        f = open(filePath, encoding='utf-8')
        doc = f.read()
        f.close()
        soup = bs4.BeautifulSoup(doc, 'lxml')
        doc = minidom.parse(filePath)
        try:
            title = soup.doc.title.string
            category = soup.doc.category.string
            description = soup.doc.text
            parsRes = self.tagValues(title=title, description=description, category=category)
        except Exception as e:
            print(title + '\n' + category + '\n' + description)
            print('Error:: ' + str(e))
            traceback.print_exc(file=sys.stdout)
        return parsRes


class Classificator(TextsData):
    def __init__(self):
        super(Classificator, self).__init__()
        self.trainFrame = pd.DataFrame(None, None)
        self.testFrame = pd.DataFrame(None, None)
        self.numWords = 15000   # кол-во слов для токенизатора
        self.maxTextLen = 100   # максимальная длинна текста
        self.classCount = 9     # кол-во классов

    def getTrainAndTestLists(self):
        trainList = []
        testList = []
        countTexts = self.statistics()
        sqlMess = """SELECT categoryId, itemTitle, itemDescription FROM goods
        WHERE categoryId = '{catId}'
        LIMIT {limit}"""
        for tup in countTexts:
            countTest = round(int(tup.countTexts)*0.1)
            countTrain = int(tup.countTexts) - countTest
            trainSample = self.cur.execute(sqlMess.format(catId=tup.classCat, limit=str(countTrain))).fetchall()
            testSample = self.cur.execute(sqlMess.format(catId=tup.classCat, limit=str(countTrain) + ',' + str(tup.countTexts))).fetchall()
            for item in trainSample:
                trainLine = []
                trainLine = [item[0], item[1], item[2]]
                trainList.append(trainLine)
            for item in testSample:
                testLine = []
                testLine = [item[0], item[1], item[2]]
                testList.append(testLine)
        self.trainFrame = pd.DataFrame(trainList, columns=['class', 'title', 'text'])
        self.testFrame = pd.DataFrame(testList, columns=['class', 'title', 'text'])

    def trainClassificator(self):
        yTrain = utils.to_categorical(self.trainFrame['class'] - 1, self.classCount)
        tokenizer = Tokenizer(num_words=self.numWords)
        tokenizer.fit_on_texts(self.trainFrame['text'])
        sequences = tokenizer.texts_to_sequences(self.trainFrame['text'])
        xTrain = pad_sequences(sequences, maxlen=self.maxTextLen)

        model_cnn = Sequential()
        model_cnn.add(Embedding(self.numWords, 32, input_length=self.maxTextLen))
        model_cnn.add(Conv1D(250, 5, padding='valid', activation='relu'))
        model_cnn.add(GlobalMaxPooling1D())
        model_cnn.add(Dense(128, activation='relu'))
        model_cnn.add(Dense(9, activation='softmax'))

        model_cnn.compile(optimizer='adam',
                          loss='categorical_crossentropy',
                          metrics=['accuracy'])

        model_cnn.summary()

        model_cnn_save_path = 'best_model_cnn.h5'
        checkpoint_callback_cnn = ModelCheckpoint(model_cnn_save_path,
                                                  monitor='val_accuracy',
                                                  save_best_only=True,
                                                  verbose=1)

        history_cnn = model_cnn.fit(xTrain,
                                    yTrain,
                                    epochs=20,
                                    batch_size=880,
                                    validation_split=0.1,
                                    callbacks=[checkpoint_callback_cnn])

        plt.plot(history_cnn.history['accuracy'],
                 label='Доля верных ответов на обучающем наборе')
        plt.plot(history_cnn.history['val_accuracy'],
                 label='Доля верных ответов на проверочном наборе')
        plt.xlabel('Эпоха обучения')
        plt.ylabel('Доля верных ответов')
        plt.legend()
        plt.show()

        test_sequences = tokenizer.texts_to_sequences(self.testFrame['text'])
        xTest = pad_sequences(test_sequences, maxlen=self.maxTextLen)
        yTest = utils.to_categorical(self.testFrame['class'] - 1, self.classCount)
        model_cnn.load_weights(model_cnn_save_path)
        model_cnn.evaluate(xTest, yTest, verbose=1)
        print()

    def run(self):
        self.getTrainAndTestLists()
        self.trainClassificator()


def runDbInserts(db, xmlReader, xmlFolder):
    for root, dirs, files in os.walk(xmlFolder):
        for file in files:
            if db.checkClass(re.match('[аА-яЯ\s]+', file.lower()).group().strip()):
                curRoute = os.path.join(root, file)
                parsRes = xmlReader.readXml(curRoute)
                if (parsRes.title != None) and (parsRes.description != None) and (parsRes.category != None):
                    db.goodsInsert(parsRes.title.strip(), parsRes.description.strip(), parsRes.category.lower().strip())



db = TextsData()
xmlReader = XmlParser()
dataPrepare = Classificator().run()
#dataPrepare.getTrainAndTestLists()
xmlFolder = 'C:\\Users\\Vlad\\PycharmProjects\\ozon-categorys\\textsWithDescription'
#runDbInserts(db, xmlReader, xmlFolder)
#db.statistics()



