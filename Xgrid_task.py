
# coding: utf-8

# In[1]:

from collections import defaultdict
import validators as va
import sqlite3
from sqlite3 import OperationalError
from urlparse import urlparse
import os.path
import json
from flask import jsonify
from flask import Flask, render_template,request


class UrlShorter:
    
    def __init__(self, url=""):
        
        self.url=url
        myPrefix="https://www.test.xg/"
        self.myPrefix=myPrefix
        self.dbName="urls.db"
        #definfing base dictionary
        self.base64Char= "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"
        self.baseDict= defaultdict(int)
        self.baseLength= len(self.base64Char)
        
        self.createDB()
        for index, value in enumerate(self.base64Char):
            self.baseDict[value]=index

    def createDB(self):
        if not os.path.exists(self.dbName):
            conn=sqlite3.connect(self.dbName)
            print "db opened"
            
            table= """CREATE TABLE MY_URLS ( ID  INTEGER PRIMARY KEY AUTOINCREMENT,
                        URL  TEXT    NOT NULL );"""
            conn.execute(table)
            print "db made"
            conn.close()
        else:
            print "DB already exists"
            return True
            
        
    def getDBConnection(self):
        
        if os.path.exists(self.dbName):
            conn=sqlite3.connect(self.dbName)
            return conn
        else:
            return False
        
    def saveToDB(self):
        return
        
    def encode(self, toEncode):
        
        if not toEncode:
            return self.base64Char[0]
        
        encoding=""
        while toEncode:
            toEncode, reminder=divmod(toEncode, self.baseLength)
            encoding = self.base64Char[reminder] + encoding
            
        return self.myPrefix+encoding
    

    
    def decode(self, toDecode):
        value=0
        for char in toDecode:
            value= value * self.baseLength + self.baseDict[char]
        return value
    
    
    #checking if url is valid or not
    def isUrl(self, urlString):
     
        url= urlparse(urlString)
        if url.scheme == "":
            urlString= "http://"+urlString
        
        if va.url(urlString):
            return urlString,True
        else:
            return "" , False
        
    def getShortUrl(self,urlString):
        """Returns the database ID of the url if it exists"""
        
        conn=self.getDBConnection()
        
        query="SELECT count(*), ID, URL from MY_URLS where URL='{}';"
        query= query.format(urlString)
        print "q1: ",query
        cursor = conn.execute(query)
        data=cursor.fetchone()
        if data[0]==0:
            query="INSERT INTO MY_URLS (URL) VALUES ('{}');"
            query= query.format(urlString)
            print "q2:",query
            res=conn.execute(query)
            conn.commit()
            print "Records created successfully"
            conn.close()
            return self.encode(res.lastrowid);
            
        else:
           
            print "data: ",data
            urlId=data[1]
            return self.encode(urlId)
            
    
    def getFullUrl(self, urlString):
        url= urlparse(urlString)
        urlId= url.path[1:]
        conn=self.getDBConnection()
        query="SELECT ID, URL from MY_URLS where ID={};"
        query= query.format(urlId)
        print "q4: ",query
        cursor = conn.execute(query)
        data=cursor.fetchone()
        print "a: ",data
        conn.close()
        return data[1]
        
    def createUrl(self,urlString):
        urlString , res = self.isUrl(urlString)
        
        if res== True:
            return self.getShortUrl(urlString)
        else:
            return False 


# In[4]:

shortner=UrlShorter()

app = Flask("__name__")

@app.route('/')
def index():
    return render_template("index.html")

    
@app.route('/getURL/<path:index>')
def user(index):
   
    
    qString=request.query_string
    
    if not qString== "":
        index= index+ "?" + qString
    index=shortner.createUrl(index)
    
    array=[]
    array.append(index)
    print array
    data=json.dumps(array)
    return data


if __name__ == "__main__":
    app.run()
