from datetime import datetime
from mongoengine import Document
from mongoengine.fields import (
    DateTimeField, ReferenceField, StringField, IntField
)

# --- User model for user collection --- #
class User(Document):
    meta = {'collection' : 'user'}
    username = StringField()
    email = StringField(required=True)
    password = StringField(required=True)

# --- OperationType model for operation_type collection --- #
class OperationType(Document):
    meta = {'collection' : 'operation_type'}
    nameOp = StringField()

# --- Operation model for operation collection --- #
class Operation(Document):
    meta = {'collection' : 'operation'}
    text = StringField(required=True)
    textType = StringField(default='input')
    result = StringField()
    dateCr = DateTimeField(default=datetime.now)
    user = ReferenceField(User)
    operation_type = ReferenceField(OperationType)

# --- Data model for data collection --- #
class Data(Document):
    meta = {'collection' : 'data'}
    url = StringField()
    title = StringField()
    content = StringField()
    datePost = StringField()
    language = StringField(default='arabic')
    score = IntField()
    classe = IntField()

# --- DataOperation model for data_operation collection --- #
class DataOperation(Document):
    meta = {'collection' : 'data_operation'}
    operation = ReferenceField(Operation)
    data = ReferenceField(Data)