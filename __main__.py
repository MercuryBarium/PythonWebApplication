from model.infogathering.webscraper import scrape
from model.matlista import vecka
import pymysql
from base64 import b64encode, b64decode

'''week = vecka(str(scrape('http://www.gladakocken.net/veckans-lunchmeny/', 'tr')))


for day in week:
    print(day.getDag())
    for ratt in day.getRatter():
        print(ratt)

#db = pymysql.connect('localhost', 'foodtruck', 'qwerty123', 'matlista')

'''

s = b64encode('something@mail.com'.encode('utf-8')).decode('utf-8')
print(s)
f = b64decode(s.encode('utf-8')).decode('utf-8')
print('\n{}'.format(f))