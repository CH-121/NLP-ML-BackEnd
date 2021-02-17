import pymongo
from mongoengine import connect
import pandas as pd
import re
import string
import csv
import pickle
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

# --- Function to get collected data from database --- #
def getDataFromDB():
    try:
        # --- Connection to Mongodb --- #
        mongo = pymongo.MongoClient(
        host = "localhost",
        port = 27017,
        serverSelectionTimeoutMS = 1000,
        )
        db = mongo.ml_project

        # --- Connection to our database --- #
        connect('ml_project', host='mongodb://localhost', alias='default')

        # --- Getting data from data collection (table) --- #
        cursor = db['data'].find()

        ids = [] # Array to store ids
        title = ' ' # Variable to store temporary the title of each row
        content = ' ' # Variable to store temporary the content of each row
        scores = [] # Array to store the scores
        classes = [] # Array to store classes
        combined_title_content = [] # Array to store combined title and content of each row
    
        # --- Loop --- #
        for document in cursor: 
            ids.append(document['_id'])
            title = document['title']
            content = document['content']
            combine = title + " " + content
            combined_title_content.append(combine)
            scores.append(document['score'])
            classes.append(document['classe'])
   
        # --- Put collected information into a Json form (keys: ids, values: combined_title_content) --- #
        content_by_id = {}
        for i, eid in enumerate(ids):
            content_by_id[eid] = combined_title_content[i]

        return {'content': content_by_id, 'score': scores, 'class': classes}

    except Exception as ex:
      print(ex)

# --- Put the list of combined_title_data from a list of text into a string format --- #
def putIntoString(listOfText):
    string_text = ''.join(listOfText)
    return string_text

# --- Function to put our collected data into a pandas DataFrame --- #
def putDataInDataFrame(string_text):
    data_df = pd.DataFrame.from_dict(string_text).transpose()
    data_df.columns = ['content']
    data_df = data_df.sort_index()
    return data_df

# --- Function to clean the data --- #
def cleanData(text):
    text = re.sub('\[.*?\]', '', text) # Remove everything between []
    text = re.sub('\(.*?\)', '', text) # Remove everything between ()
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text) # Remove punctuation
    text = re.sub('\w*\d\w*', '', text) # Remove numbers
    text = re.sub('[‘’“”«»…]', '', text) # Remove specific caracters
    text = re.sub("-_،؟ ً َّ ًّ ّ ٌّ َ ً ُ ٌ ٍ ِ ْ ٍّ ِّ", '', text) # Remove specific arabic caracters
    text = re.sub('\n', '', text) # Remove '\n'
    return text

# --- Function to organize the Dataframe (adding scores and classes columns) --- #
def organizeData(data_df, scores, classes, cleaned_data):
    # --- Adding score and class columns --- #
    data_df['score'] = scores
    data_df['class'] = classes
    return data_df

# --- Training models class (KNN, DT, ANN, NB, SVM) --- #
class TrainingModels:
    organized_data = ''

    # --- Training model function --- #
    def train(organized_data):
        features = ['content', 'score', 'class']
        organized_data = organized_data.drop_duplicates() # Remove duplicated rows
        organized_data.reset_index(drop=True, inplace=True) # Remove dataframe indexes
        Y = organized_data['class'].values # We fixe the column class in Y
        X = organized_data.drop(columns=['class']) # We drop it in X

        X_train, X_test, Y_train, Y_test = train_test_split(organized_data['content'], Y, test_size=0.3)

        pipe = Pipeline([('vect', CountVectorizer()),
                 ('tfidf', TfidfTransformer()),
                 ('model', SVC() )]) # Learning algorithm used : Support Vector Machine (SVM)

        # Fitting the model
        model = pipe.fit(X_train, Y_train)

        # Saving model
        pickle.dump(model, open('model.sav', 'wb'))

        # Prediction of X_test
        prediction = model.predict(X_test)
        print(prediction)

        # Accuracy
        print("SVC accuracy: {}%".format(round(accuracy_score(Y_test, prediction)*100,2)))
        return model
    
    # --- Prediction function --- #
    def predict(model, text):
        prediction = model.predict([text])
        return prediction

# --- Main function --- #
"""
if __name__ == '__main__':
    # --- Getting and cleaning data --- #
    data = getDataFromDB()['content']
    string_text = {key: [putIntoString(value)] for (key, value) in data.items()}
    data_df = putDataInDataFrame(string_text)
    data_cleaning = lambda x: cleanData(x)

    # --- Organizing data in a pandas dataframe --- #
    cleaned_data = pd.DataFrame(data_df.content.apply(data_cleaning))
    organized_data = organizeData(data_df, getDataFromDB()['score'], getDataFromDB()['class'], cleaned_data)

    # --- Training data --- #
    model = TrainingModels.train(organized_data)
    prediction = TrainingModels.predict(model, "كورونا خطيرة")
    # print(prediction)
"""