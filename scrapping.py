#coding:utf-8
import requests
from bs4 import BeautifulSoup
from flask import Flask, Response, request
import pymongo
import json
import csv
from models import Data
from mongoengine import connect

class scrapping():
    # --- Collecting data from the URL --- #
    def getDataFromURL(url):
        source = requests.get(url).text
        soup = BeautifulSoup(source, 'lxml')
        return soup

    # --- Save collected data in a .csv file --- #
    def fileSave(fileName, url,className):
        csv_file = open(fileName+'.csv', 'w', encoding="utf-8")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['titre', 'content_link'])
        soup=scrapping.getDataFromURL(url)
        content_link = []
        for article in soup.find_all('div', class_=className):
            titre = article.h1.text
            try:
                for art in article.findAll('p'):
                    content_link += ' ' + art.text

            except Exception as e:
                content_link = None

            csv_writer.writerow([titre, content_link])

        csv_file.close()

    # --- Save collected data in Mongodb database --- #
    def dbSave(url, className):
        try:
          mongo = pymongo.MongoClient(
            host = "localhost",
            port = 27017,
            serverSelectionTimeoutMS = 1000,
          )
          db = mongo.ml_project
          soup = scrapping.getDataFromURL(url)

        # --- Save data from div ---
          content= ''
          for article in soup.find_all('div', class_=className):
              titre = article.h1.text
              try:
                  for art in article.findAll('p'):
                      content += ' '+art.text

              except Exception as e:
                  content = None

              # --- Save data in database ---
              data = {"url":url, "title":titre,"content": content}
              dbResponse = db.data.insert_one(data)
              print(dbResponse.inserted_id)

          return Response(
            response = json.dumps({"message":"data saved","id":f"{dbResponse.inserted_id}"}),
            status = 200,
            mimetype = "application/json"
          )
        except Exception as ex:
          print(ex)

    # --- Save data from Lakom --- #
    def dbSaveLakom(url):
        try:
            
          mongo = pymongo.MongoClient(
            host = "localhost",
            port = 27017,
            serverSelectionTimeoutMS = 1000,
          )
          db = mongo.ml_project
          soup=scrapping.getDataFromURL(url)

          try:
              for title in soup.find_all('div', class_= 'title'):
                  titre = title.h3.text
              content = soup.find('strong').text
              
          except Exception as e:
                  content = None    
          
          #   --- Save data in database ---
          data = {"url":url, "title":titre,"content": content, "language" : "arabic", "datePost": "now" ,"score" : 4, "classe" : 1}
          dbResponse = db.data.insert_one(data)
          print(dbResponse.inserted_id)

          return Response(
            response = json.dumps({"message":"data saved","id":f"{dbResponse.inserted_id}"}),
            status = 200,
            mimetype = "application/json"
          )
        except Exception as ex:
          print(ex)

    # --- Save data from Alakhbar --- #
    def dbSaveAlakhbar(url):
        try:
            
          mongo = pymongo.MongoClient(
            host = "localhost",
            port = 27017,
            serverSelectionTimeoutMS = 1000,
          )
          db = mongo.ml_project
          soup=scrapping.getDataFromURL(url)

          try:

            titre = soup.find('h1', class_= 'post-title entry-title' ).text
            datePost = soup.find('span', class_= 'date meta-item tie-icon' ).text
            content = soup.find('p').text

          except Exception as e:
                  content = None
          
          #   --- Save data in database ---
          data = {"url":url, "title":titre,"content": content, "language" : "arabic", "datePost": datePost ,"score" : 4, "classe" : 1}
          dbResponse = db.data.insert_one(data)
          print(dbResponse.inserted_id)

          return Response(
            response = json.dumps({"message":"data saved","id":f"{dbResponse.inserted_id}"}),
            status = 200,
            mimetype = "application/json"
          )
        except Exception as ex:
          print(ex)

    # --- Save data from Akhbarona --- #
    def dbSaveAkhbarona(url):
      try:
          
        mongo = pymongo.MongoClient(
          host = "localhost",
          port = 27017,
          serverSelectionTimeoutMS = 1000,
        )
        db = mongo.ml_project
        soup = scrapping.getDataFromURL(url)
        try:

          titre = soup.find('h1', class_='page_title').text
          datePost = soup.find('span', class_='story_date').text
          content = soup.find('div', {'id' : 'article_body'}).text

        except Exception as e:
                content = None
        
        #   --- Save data in database ---
        data = {"url":url, "title":titre,"content": content, "language" : "arabic", "datePost": datePost ,"score" : 2, "classe" : 1}
        dbResponse = db.data.insert_one(data)
        print(dbResponse.inserted_id)

        return Response(
          response = json.dumps({"message":"data saved","id":f"{dbResponse.inserted_id}"}),
          status = 200,
          mimetype = "application/json"
        )
      except Exception as ex:
        print(ex)

    # --- Save data from Assahraa --- #
    def dbSaveAssahraa(url):
      try:
          
        mongo = pymongo.MongoClient(
          host = "localhost",
          port = 27017,
          serverSelectionTimeoutMS = 1000,
        )
        db = mongo.ml_project
        soup = scrapping.getDataFromURL(url)
        try:

          titre = soup.find('div', class_='col-sm-12 sec-info').h1.text
          datePost = soup.find('div', class_='time').text
          content = soup.find('div', class_='col-sm-12 article').text.strip()
          # print(content)

        except Exception as e:
                content = None
        
        #   --- Save data in database ---
        data = {"url":url, "title":titre,"content": content, "language" : "arabic", "datePost": datePost ,"score" : 3, "classe" : 1}
        dbResponse = db.data.insert_one(data)
        print(dbResponse.inserted_id)

        return Response(
          response = json.dumps({"message":"data saved","id":f"{dbResponse.inserted_id}"}),
          status = 200,
          mimetype = "application/json"
        )
      except Exception as ex:
        print(ex)

    # --- Save data from Al3omk --- #
    def dbSaveAl3omk(url):
      try:

        mongo = pymongo.MongoClient(
          host = "localhost",
          port = 27017,
          serverSelectionTimeoutMS = 1000,
        )
        db = mongo.ml_project
        soup = scrapping.getDataFromURL(url)
        try:

          titre = soup.find('h1', class_='title-single').text
          # print(titre)
          datePost = soup.find('span', class_='timePost').text
          # print(datePost)
          content = soup.find('div', class_='post_content').p.text.strip()
        except Exception as e:
                content = None
        
        #   --- Save data in database ---
        data = {"url":url, "title":titre,"content": content, "language" : "arabic", "datePost": datePost ,"score" : 4, "classe" : 1}
        dbResponse = db.data.insert_one(data)
        print(dbResponse.inserted_id)

        return Response(
          response = json.dumps({"message":"data saved","id":f"{dbResponse.inserted_id}"}),
          status = 200,
          mimetype = "application/json"
        )
      except Exception as ex:
        print(ex)

# if(__name__=='__main__'):
#   connect('ml_project', host='mongodb://localhost', alias='default')
  # ----------------- Scrapping examples ----------------- #
  # scrapping.dbSave(url='https://ar.hibapress.com/details-281066.html', className='main-content tie-col-md-8 tie-col-xs-12')
  # scrapping.dbSaveLakom('https://lakome2.com/covid19/216900/')
  # scrapping.dbSaveLakom('https://lakome2.com/covid19/216712/')
  # scrapping.dbSaveLakom('https://lakome2.com/covid19/216903/')
  # scrapping.dbSaveLakom('https://lakome2.com/covid19/216917/')
  # scrapping.dbSaveLakom('https://lakome2.com/covid19/216911/')
  # scrapping.dbSaveLakom('https://lakome2.com/societe/216913/')
  # scrapping.dbSaveLakom('https://lakome2.com/flash-infos/216797/')
  # scrapping.dbSaveLakom('https://lakome2.com/covid19/216760/')
  # scrapping.dbSaveLakom('https://lakome2.com/covid19/216720/')
  # scrapping.dbSaveLakom('https://lakome2.com/covid19/216764/')
  # scrapping.dbSaveLakom('https://lakome2.com/flash-infos/216555/')
  # scrapping.dbSaveLakom('https://lakome2.com/flash-infos/216598/')
  # scrapping.dbSaveLakom('https://lakome2.com/covid19/216632/')
  # scrapping.dbSaveLakom('https://lakome2.com/covid19/216408/')
  # scrapping.dbSaveLakom('https://lakome2.com/covid19/216413/')
  # scrapping.dbSaveLakom('https://lakome2.com/covid19/216468/')
  # scrapping.dbSaveLakom('https://lakome2.com/politique/216525/')