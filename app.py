from flask import Flask
from nltk.tokenize import word_tokenize
import numpy as np
import pandas as pd
import requests
import sklearn
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
from nltk import sent_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
import json, codecs
from json import JSONEncoder
from flask_graphql import GraphQLView
from database import init_db
from schema import schema
import graphene
import re
from flask_cors import CORS
import string
from training import TrainingModels
import pickle
from textblob import TextBlob

app = Flask(__name__) # Create an app
CORS(app)

# --- GraphQL URL and View --- #
app.add_url_rule('/graphql',
    view_func = GraphQLView.as_view('graphql', schema = schema, graphiql=True)
)

# --- Tokenization --- #
class Tokenization(graphene.ObjectType):
  txt = graphene.String()
  def resolve_txt(root, info):
    text = info.context.get('txt')
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub('[‘’“”«»…]', '', text)
    text = re.sub("-_،؟", '', text)
    word_tokens = word_tokenize(text)
    return {"result":word_tokens}

# --- Stop Words --- #
class StopWords(graphene.ObjectType):
  txt = graphene.String()
  def resolve_txt(root, info):
    stop_words = set(stopwords.words('arabic'))
    text = info.context.get('txt')
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub('[‘’“”«»…]', '', text)
    text = re.sub("-_،؟", '', text)
    word_tokens = word_tokenize(text)
    without_stop_words = [w for w in word_tokens if not w in stop_words]
    return {"result":without_stop_words}

# --- Lemmatization --- #
class Lemmatization(graphene.ObjectType):
  txt = graphene.String()
  def resolve_txt(root, info):
    text = info.context.get('txt') #.encode('utf8')
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub('[‘’“”«»…]', '', text)
    text = re.sub("-_،؟", '', text)
    lemmatizer = WordNetLemmatizer()
    word_tokens = word_tokenize(text)
    lemmatized = []
    for word in word_tokens:
      lemmatized.append(nltk.ISRIStemmer().suf32(word))
    return {"result":lemmatized}

# --- Stemming --- #
class Stemming(graphene.ObjectType):
  txt = graphene.String()
  def resolve_txt(root, info):
    text = info.context.get('txt') #.encode('utf8')
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub('[‘’“”«»…]', '', text)
    text = re.sub("-_،؟", '', text)
    stemmer = PorterStemmer()
    word_tokens = word_tokenize(text)
    stemmed = []
    for word in word_tokens:
      stemmed.append(stemmer.stem(word))
    return {"result":stemmed}

# --- Pos Tagging --- #
class PosTagging(graphene.ObjectType):
  txt = graphene.String()
  def resolve_txt(root, info):
    stop_words = set(stopwords.words('arabic'))
    text = info.context.get('txt')
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub('[‘’“”«»…]', '', text)
    text = re.sub("-_،؟", '', text)
    word_tokens = sent_tokenize(text)
    for i in word_tokens:
      word_list = nltk.word_tokenize(i)
      word_list = [word for word in word_list if not word in stop_words]
      tagged = nltk.pos_tag(word_list)
    return {"result":tagged}

# --- Bag of words --- #
class BagOfWords(graphene.ObjectType):
  txt = graphene.String()
  def resolve_txt(root, info):
    text = info.context.get('txt')
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub('[‘’“”«»…]', '', text)
    text = re.sub("-_،؟", '', text)
    txt = [text]
    vect = CountVectorizer()
    vect.fit(txt)
    to_array = vect.transform(txt).toarray()
    bag_of_words = to_array.tolist()
    return {"result":bag_of_words}

# --- Route for Tokenization --- #
@app.route("/tokenization/<text>", methods=['get'])
def tokenize(text):
  schema = graphene.Schema(Tokenization)
  result = schema.execute('{ txt }', context={'txt': text})
  data = result.data['txt'].replace("\'", "\"")
  res = json.dumps(json.loads(data)["result"], ensure_ascii=False).encode('utf8')
  res = res.decode()
  res = res.replace("\"", "")
  res = res.replace("[", "")
  res = res.replace("]", "")
  return {'result':res}

# --- Route for Stop Words --- #
@app.route("/stopwords/<text>", methods=['get'])
def stopword(text):
  schema = graphene.Schema(StopWords)
  result = schema.execute('{ txt }', context={'txt': text})
  data = result.data['txt'].replace("\'", "\"")
  res = json.dumps(json.loads(data)["result"], ensure_ascii=False).encode('utf8')
  res = res.decode()
  res = res.replace("\"", "")
  res = res.replace("[", "")
  res = res.replace("]", "")
  return {'result':res}

# --- Route for Lemmatization --- #
@app.route("/lemmatization/<text>", methods=['get'])
def lemmatize(text):
  schema = graphene.Schema(Lemmatization)
  result = schema.execute('{ txt }', context={'txt': text})
  data = result.data['txt'].replace("\'", "\"")
  res = json.dumps(json.loads(data)["result"], ensure_ascii=False).encode('utf8')
  res = res.decode()
  res = res.replace("\"", "")
  res = res.replace("[", "")
  res = res.replace("]", "")
  return {'result':res}

# --- Route for Stemming --- #
@app.route("/stemming/<text>", methods=['get'])
def stem(text):
  schema = graphene.Schema(Stemming)
  result = schema.execute('{ txt }', context={'txt': text})
  data = result.data['txt'].replace("\'", "\"")
  res = json.dumps(json.loads(data)["result"], ensure_ascii=False).encode('utf8')
  res = res.decode()
  res = res.replace("\"", "")
  res = res.replace("[", "")
  res = res.replace("]", "")
  return {'result':res}

# --- Route for Pos Tagging --- #
@app.route("/postagging/<text>", methods=['get'])
def postag(text):
  schema = graphene.Schema(PosTagging)
  result = schema.execute('{ txt }', context={'txt': text})
  da = result.data['txt'].replace("\'", "\"")
  dat = da.replace("(", "[")
  data = dat.replace(")", "]")
  res = json.dumps(json.loads(data)["result"], ensure_ascii=False).encode('utf8')
  res = res.decode()
  res = res.replace("\"", "")
  res = res.replace("[", "")
  res = res.replace("]", "")
  return {'result':res}

# --- Route for Bag of Words --- #
@app.route("/bagofwords/<text>", methods=['get'])
def bagofwords(text):
  schema = graphene.Schema(BagOfWords)
  result = schema.execute('{ txt }', context={'txt': text})
  data = result.data['txt'].replace("\'", "\"")
  res = json.dumps(json.loads(data)["result"], ensure_ascii=False).encode('utf8')
  res = res.decode()
  res = res.replace("\"", "")
  res = res.replace("[", "")
  res = res.replace("]", "")
  return {'result':res}

# --- Route for Fake News --- #
@app.route("/fakenews/<text>", methods=['get'])
def fakenews(text):
  model = pickle.load(open('model.sav', 'rb'))
  prediction = TrainingModels.predict(model, text)
  prediction = prediction.tolist()
  prediction = json.dumps(prediction)
  prediction = prediction.replace("[", "")
  prediction = prediction.replace("]", "")
  return {'result': prediction}

# --- Route for Sentiment Analysis --- #
@app.route("/sentimentanalysis/<text>")
def sentiment(text):
  obj = TextBlob(text)
  sentiment = obj.sentiment.polarity
  sentiment = json.dumps(sentiment)
  sentiment = sentiment.replace("[", "")
  sentiment = sentiment.replace("]", "")
  return {'result': sentiment}
  
# --- To run the application when runnig the python file: "py app.py" ---
if __name__ == "__main__":
  app.run(debug=True)

# Note: to run the application, you can use instead of the main function 
# the following command line : "py -m flask run"