import graphene
from graphene.relay import Node
from graphene_mongo import MongoengineConnectionField, MongoengineObjectType
from models import User as UserModel
from models import OperationType as OperationTypeModel
from models import Operation as OperationModel
from models import DataOperation as DataOperationModel
from models import Data as DataModel
from mongoengine.queryset.visitor import Q
from bson.objectid import ObjectId
from nltk.tokenize import word_tokenize
import re
import string
import json
from io import StringIO
from nltk.corpus import stopwords
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.stem import PorterStemmer
from nltk import sent_tokenize
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from mongoengine.fields import IntField, StringField, ObjectIdField

# --- User object ---
class User(MongoengineObjectType):
    class Meta:
        model = UserModel

# --- OperationType object --- #
class OperationType(MongoengineObjectType):
    class Meta:
        model = OperationTypeModel

# --- Operation object --- #
class Operation(MongoengineObjectType):
    class Meta:
        model = OperationModel

# --- Data object --- #
class Data(MongoengineObjectType):
    class Meta:
        model = DataModel

# --- DataOperation object --- #
class DataOperation(MongoengineObjectType):
    class Meta:
        model = DataOperationModel

# --- Class for Queries --- #
class Query(graphene.ObjectType):
    # --- Queries for extracting data from database --- #
    users = graphene.List(User)
    operation_types = graphene.List(OperationType)
    operations = graphene.List(Operation)
    datas = graphene.List(Data)

    user_operations = graphene.List(Operation, idUser=graphene.String())
    user_login = graphene.Field(User, email=graphene.String(), password=graphene.String())
    user_email_exist = graphene.Field(User, email=graphene.String())
    data_true = graphene.List(Data, title=graphene.String())

    # --- Resolvers --- #
    def resolve_users(self, info):
        return list(UserModel.objects.all())

    def resolve_operation_types(self, info):
        return list(OperationTypeModel.objects.all())

    def resolve_operations(self, info):
        return list(OperationModel.objects.all())

    def resolve_datas(self, info):
        return list(DataModel.objects.all())

    def resolve_user_operations(self, info, idUser):
        return OperationModel.objects.filter(Q(user=idUser))
    
    def resolve_user_login(self, info, email, password):
        return UserModel.objects.get(Q(email=email)&Q(password=password))
        
    def resolve_user_email_exist(self, info, email):
        return UserModel.objects.get(Q(email=email))

    def resolve_data_true(self, info, title):
        rgx = re.compile('.*'+title+'.*')
        return DataModel.objects.filter(Q(title=rgx)&Q(classe=1)) #.limit(10)

# --- Class for creating a user --- #
class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String()
        email = graphene.String()
        password = graphene.String()

    user = graphene.Field(lambda: User)
    def mutate(self, info, username, email, password):
        user = UserModel(username = username, email = email, password = password)
        user.save()
        return CreateUser(user = user)

# --- Class for creating an operation --- #
class CreateOperation(graphene.Mutation):
    class Arguments:
        text = graphene.String()
        textType = graphene.String()
        # result = graphene.String()
        user_id = graphene.String()
        operation_type = graphene.String()

    operation = graphene.Field(lambda: Operation)
    def mutate(self, info, text, textType, user_id, operation_type):
        listOpTypes = list(OperationTypeModel.objects.all())
        for opType in listOpTypes:
            if opType.id == ObjectId(str(operation_type)):
                nameOp = opType.nameOp
                break
            # else:
            #     print("I can't find it !")
        if nameOp == "Tokenization":
            result = tokenize(text)
        if nameOp == "Stop words":
            result = stopword(text)
        if nameOp == "Lemmatization":
            result = lemmatize(text)
        if nameOp == "Stemming":
            result = stem(text)
        if nameOp == "Pos Tagging":
            result = postag(text)
        if nameOp == "Bag of words":
            result = bagofwords(text)
        if nameOp == "TF-IDF":
            result = tfidf(text)
        if nameOp == "Word2Vec":
            pass
        operation = OperationModel(text = text, textType=textType, result = result, user= user_id, operation_type= operation_type)
        
        operation.save()
        return CreateOperation(operation = operation)

# --- Class for deleting a user --- #
class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.String()
    
    user = graphene.Field(lambda: graphene.List(User), id=graphene.String())
    def mutate(self, info, id):
        # --- Getting the user with this id --- #
        user = UserModel.objects(id=ObjectId(str(id)))
        # --- Getting and deleting operation done by this user --- #
        for operation in OperationModel.objects(user=ObjectId(str(id))):
            operation.delete()
        user.delete()
        return DeleteUser(user = user)

# --- Class for deleting an operation --- #
class DeleteOperation(graphene.Mutation):
    class Arguments:
        id = graphene.String()
    
    operation = graphene.Field(lambda: graphene.List(Operation), id=graphene.String())
    def mutate(self, info, id):
        # --- Getting the operation with this id --- #
        operation = OperationModel.objects(id=ObjectId(str(id)))
        # --- Getting and deleting data_operations with id_operation equal to this id --- #
        for data_operation in DataOperationModel.objects(operation=ObjectId(str(id))):
            data_operation.delete()
        operation.delete()
        return DeleteUser(user = operation)

# --- Class for Mutations --- #
class Mutations(graphene.ObjectType):
    create_user = CreateUser.Field()
    create_operation = CreateOperation.Field()
    delete_user = DeleteUser.Field()
    delete_operation = DeleteOperation.Field()

# -------------------------- NLP Services -------------------------- #
# --- Tokenization --- #
class Tokenization(graphene.ObjectType):
  txt = graphene.String()
  def resolve_txt(root, info):
    text = info.context.get('txt')
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    word_tokens = word_tokenize(text)
    return {"result":word_tokens}

def tokenize(text):
  schema_ = graphene.Schema(Tokenization)
  result = schema_.execute('{ txt }', context={'txt': text})
  data = result.data['txt'].replace("\'", "\"")
  res = json.dumps(json.loads(data)["result"], ensure_ascii=False).encode('utf8')
  res = res.decode()
  res = res.replace("\"", "")
  res = res.replace("[", "")
  res = res.replace("]", "")
  return res

# --- Stop Words --- #
class StopWords(graphene.ObjectType):
  txt = graphene.String()
  def resolve_txt(root, info):
    stop_words = set(stopwords.words('arabic'))
    text = info.context.get('txt')
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    word_tokens = word_tokenize(text)
    without_stop_words = [w for w in word_tokens if not w in stop_words]
    return {"result":without_stop_words}

def stopword(text):
  schema = graphene.Schema(StopWords)
  result = schema.execute('{ txt }', context={'txt': text})
  data = result.data['txt'].replace("\'", "\"")
  res = json.dumps(json.loads(data)["result"], ensure_ascii=False).encode('utf8')
  res = res.decode()
  res = res.replace("\"", "")
  res = res.replace("[", "")
  res = res.replace("]", "")
  return res

# --- Lemmatization --- #
class Lemmatization(graphene.ObjectType):
  txt = graphene.String()
  def resolve_txt(root, info):
    text = info.context.get('txt') #.encode('utf8')
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    lemmatizer = WordNetLemmatizer()
    word_tokens = word_tokenize(text)
    lemmatized = []
    for word in word_tokens:
      lemmatized.append(nltk.ISRIStemmer().suf32(word))
    return {"result":lemmatized}

def lemmatize(text):
  schema = graphene.Schema(Lemmatization)
  result = schema.execute('{ txt }', context={'txt': text})
  data = result.data['txt'].replace("\'", "\"")
  res = json.dumps(json.loads(data)["result"], ensure_ascii=False).encode('utf8')
  res = res.decode()
  res = res.replace("\"", "")
  res = res.replace("[", "")
  res = res.replace("]", "")
  return res

# --- Stemming --- #
class Stemming(graphene.ObjectType):
  txt = graphene.String()
  def resolve_txt(root, info):
    text = info.context.get('txt') #.encode('utf8')
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    stemmer = PorterStemmer()
    word_tokens = word_tokenize(text)
    stemmed = []
    for word in word_tokens:
      stemmed.append(stemmer.stem(word))
    return {"result":stemmed}

def stem(text):
  schema = graphene.Schema(Stemming)
  result = schema.execute('{ txt }', context={'txt': text})
  data = result.data['txt'].replace("\'", "\"")
  res = json.dumps(json.loads(data)["result"], ensure_ascii=False).encode('utf8')
  res = res.decode()
  res = res.replace("\"", "")
  res = res.replace("[", "")
  res = res.replace("]", "")
  return res

# --- Pos Tagging --- #
class PosTagging(graphene.ObjectType):
  txt = graphene.String()
  def resolve_txt(root, info):
    stop_words = set(stopwords.words('arabic'))
    text = info.context.get('txt')
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    word_tokens = sent_tokenize(text)
    for i in word_tokens:
      word_list = nltk.word_tokenize(i)
      word_list = [word for word in word_list if not word in stop_words]
      tagged = nltk.pos_tag(word_list)
      return {"result":tagged}

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
  return res

# --- Bag of words --- #
class BagOfWords(graphene.ObjectType):
  txt = graphene.String()
  def resolve_txt(root, info):
    text = info.context.get('txt')
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    txt = [text]
    vect = CountVectorizer()
    vect.fit(txt)
    to_array = vect.transform(txt).toarray()
    bag_of_words = to_array.tolist()
    return {"result":bag_of_words}

def bagofwords(text):
  schema = graphene.Schema(BagOfWords)
  result = schema.execute('{ txt }', context={'txt': text})
  data = result.data['txt'].replace("\'", "\"")
  res = json.dumps(json.loads(data)["result"], ensure_ascii=False).encode('utf8')
  res = res.decode()
  res = res.replace("\"", "")
  res = res.replace("[", "")
  res = res.replace("]", "")
  return res

# --- Schema --- #
schema = graphene.Schema(query = Query, mutation = Mutations, types = [User, OperationType, Operation, Data, DataOperation])