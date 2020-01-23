from model.infogathering.webscraper import scrape
from model.matlista import vecka
from model.hashing.passwording import hashNsalt, checkPW
import pymysql

week = vecka(str(scrape('http://www.gladakocken.net/veckans-lunchmeny/', 'tr')))


for day in week:
    print(day.getDag())
    for ratt in day.getRatter():
        print(ratt)

#db = pymysql.connect('localhost', 'foodtruck', 'qwerty123', 'matlista')

