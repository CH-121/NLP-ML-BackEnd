# Note: this file is used for testing queries and mutations (GraphQL-MongoDB)
# uncomment the main function and run it to test

from mongoengine import connect
from models import User, OperationType, Operation, Data,  DataOperation

# --- Connection to local database (MongoDB) ---
connect('ml_project', host='mongodb://localhost', alias='default')

# --- Test Function ---
def init_db():
    # --- Inserting a user ---
    test = User(username = 'Razan', email='razan@gmail.com', password='123')
    test.save()

    # --- Inserting some operation-types ---
    tokenization = OperationType(nameOp = 'Tokenization')
    tokenization.save()

    stopWords = OperationType(nameOp = 'Stop words')
    stopWords.save()

    lemmatization = OperationType(nameOp = 'Lemmatization')
    lemmatization.save()

    stemming = OperationType(nameOp = 'Stemming')
    stemming.save()

    posTagging = OperationType(nameOp = 'Pos Tagging')
    posTagging.save()

    bagOfWords = OperationType(nameOp = 'Bag of words')
    bagOfWords.save()

    TfIdf = OperationType(nameOp = 'TF-IDF')
    TfIdf.save()

    word2Vec = OperationType(nameOp = 'Word2Vec')
    word2Vec.save()

    # --- Inserting an operation ---
    stopWordOp1 = Operation(text="منذ انعقاد المجلس الوطني الأخير لحزب العدالة والتنمية لا حديث بين الأعضاء إلا عن أساليب التهديد والوعيد التي بات يرفعها بعض أعضاء الأمانة العامة في وجه المخالفين للقيادة الحالية.", 
    textType="input", result="['انعقاد', 'المجلس', 'الوطني', 'الأخير', 'لحزب', 'العدالة', 'والتنمية', 'حديث', 'الأعضاء', 'أساليب', 'التهديد', 'والوعيد', 'بات', 'يرفعها', 'أعضاء', 'الأمانة', 'العامة', 'وجه', 'المخالفين', 'للقيادة', 'الحالية', '.']", 
    dateCr="2012-10-15T21:26:17Z", user=test, operation_type=stopWords)
    stopWordOp1.save()

    tokenOp1 = Operation(text="منذ انعقاد المجلس الوطني الأخير لحزب العدالة والتنمية", 
    textType="input", result="[ 'منذ', 'انعقاد', 'المجلس', 'الوطني', 'الأخير', 'لحزب', 'العدالة', 'والتنمية' ]", 
    dateCr="2012-10-15T21:26:17Z", user=test, operation_type=tokenization)
    tokenOp1.save()

    # --- Inserting some datas ---
    data1 = Data(url="lakom",title="tttttttttt", content= "test", language="arabic",datePost="now", score=4, classe=1)
    data1.save()

    data2 = Data(url="lakom",title="tttttttttt", content= "test", language="arabic",datePost="now", score=4, classe=1)
    data2.save()

# --- Main function ---
# if(__name__=='__main__'):
#     init_db()