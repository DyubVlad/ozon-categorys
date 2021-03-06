import sqlite3
import traceback
import sys
import os
import re
from collections import namedtuple
import bs4


from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Embedding, Conv1D, GlobalMaxPooling1D
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras import utils
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle


class TextsData:
    def __init__(self):
        try:
            self.conn = sqlite3.connect('textsFromOzon_ver0.1.db')
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

        def delPunPunctuationAndInsig(string):
            string = re.sub(r'[^\w\s]+|[\d]+|км/ч|\b\w{0,2}\b', r' ', string)
            string = re.sub(r'\b\w{0,2}\b', r'', string)
            string = re.sub(r'\b\s+\b', r' ', string.strip())
            return string.lower()

        f = open(filePath, encoding='utf-8')
        doc = f.read()
        f.close()
        soup = bs4.BeautifulSoup(doc, "html.parser")
        try:
            title = soup.doc.title.string
            category = soup.doc.category.string
            description = soup.find(text=lambda tag: isinstance(tag, bs4.CData)).string

            if (title != None) and (description != None) and (description != '') \
                    and (category != None):
                title = delPunPunctuationAndInsig(title)
                category = soup.doc.category.string.lower().strip()
                description = description.replace('Описание', "").replace('Показать полностью', "")
                description = delPunPunctuationAndInsig(description)
                parsRes = self.tagValues(title=title, description=description, category=category)
                return parsRes
            else:
                return None
        except Exception as e:
            print('Error:: ' + str(e))
            traceback.print_exc(file=sys.stdout)



class Classificator(TextsData):
    def __init__(self):
        super(Classificator, self).__init__()
        self.trainFrame = pd.DataFrame(None, None)
        self.testFrame = pd.DataFrame(None, None)
        self.numWords = 30000   # кол-во слов для токенизатора
        self.maxTextLen = 30   # максимальная длинна текста
        self.classCount = 9     # кол-во классов
        self.modelCnnSavePath = 'best_model_cnn_ver0.2.h5'     # файл модели
        self.tokenizatorPath = 'tokenizer_ver0.2.pickle'       # файл токенизатора

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

        tokenizer.fit_on_texts(self.trainFrame['title'])
        with open(self.tokenizatorPath, 'wb') as handle:
            pickle.dump(tokenizer, handle, protocol=pickle.HIGHEST_PROTOCOL)
        sequences = tokenizer.texts_to_sequences(self.trainFrame['title'])
        xTrain = pad_sequences(sequences, maxlen=self.maxTextLen)

        model_cnn = Sequential()
        model_cnn.add(Embedding(self.numWords, 32, input_length=self.maxTextLen))
        model_cnn.add(Conv1D(250, 5, padding='valid', activation='relu'))
        model_cnn.add(GlobalMaxPooling1D())
        model_cnn.add(Dense(1128, activation='relu'))
        model_cnn.add(Dense(9, activation='softmax'))

        model_cnn.compile(optimizer='adam',
                          loss='categorical_crossentropy',
                          metrics=['accuracy'])

        model_cnn.summary()


        checkpoint_callback_cnn = ModelCheckpoint(self.modelCnnSavePath,
                                                  monitor='val_accuracy',
                                                  save_best_only=True,
                                                  verbose=1)

        history_cnn = model_cnn.fit(xTrain,
                                    yTrain,
                                    epochs=30,
                                    batch_size=900,
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

        test_sequences = tokenizer.texts_to_sequences(self.testFrame['title'])
        xTest = pad_sequences(test_sequences, maxlen=self.maxTextLen)
        yTest = utils.to_categorical(self.testFrame['class'] - 1, self.classCount)
        model_cnn.load_weights(self.modelCnnSavePath)
        model_cnn.evaluate(xTest, yTest, verbose=1)

    def runTrain(self):
        self.getTrainAndTestLists()
        self.trainClassificator()

    def getTextClass(self, text):
        textList = []
        textList.append(text)
        model = Sequential()
        model.add(Embedding(self.numWords, 32, input_length=self.maxTextLen))
        model.add(Conv1D(250, 5, padding='valid', activation='relu'))
        model.add(GlobalMaxPooling1D())
        model.add(Dense(1128, activation='relu'))
        model.add(Dense(9, activation='softmax'))

        model.compile(optimizer='adam',
                          loss='categorical_crossentropy',
                          metrics=['accuracy'])

        model.load_weights(self.modelCnnSavePath)
        with open(self.tokenizatorPath, 'rb') as handle:
            tokenizer = pickle.load(handle)
        inputSequence = tokenizer.texts_to_sequences(textList)
        prepSequence = pad_sequences(inputSequence, maxlen=self.maxTextLen)
        prediction = model.predict(prepSequence)
        return np.argmax(prediction)+1


def runDbInserts(db, xmlReader, xmlFolder):
    for root, dirs, files in os.walk(xmlFolder):
        for file in files:
            if db.checkClass(re.match('[аА-яЯ\s]+', file.lower()).group().strip()):
                curRoute = os.path.join(root, file)
                parsRes = xmlReader.readXml(curRoute)
                if parsRes != None:
                    if parsRes.description != '':
                        db.goodsInsert(parsRes.title.strip(), parsRes.description.strip(), parsRes.category.lower().strip())



def chengeData():
    db = TextsData()
    xmlReader = XmlParser()
    xmlFolder = 'C:\\Users\\Vlad\\PycharmProjects\\ozon-categorys\\textsWithDescription'
    runDbInserts(db, xmlReader, xmlFolder)

def trainModel():
    dataPrepare = Classificator().runTrain()







