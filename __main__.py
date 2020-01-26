from model.infogathering.webscraper import scrape
from model.matlista import vecka, dbconnector
import pymysql
from base64 import b64encode, b64decode

'''week = vecka(str(scrape('http://www.gladakocken.net/veckans-lunchmeny/', 'tr')))


for day in week:
    print(day.getDag())
    for ratt in day.getRatter():
        print(ratt)

#db = pymysql.connect('localhost', 'foodtruck', 'qwerty123', 'matlista')

'''
database = dbconnector('localhost', 'pythonhttp', 'qwerty123', 'matlista')
print(database.CreateNewUser('something@email.com', 'joe', 'ABC'))