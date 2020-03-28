from flask import Flask, request, redirect, make_response, jsonify
from model.matlista import basicusermanager, wristwatch
from public.view import get_html
from model.infogathering.webscraper import scrape
from model.matlista import vecka
import json, datetime
from base64 import b64encode


config = open('./email.txt', 'r').readlines()

dagar       = ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag']

email       = config[0]
password    = config[1]

backend = basicusermanager('localhost', 'pythonhttp', 'qwerty123', 'matlista', email, password)


w = wristwatch()

year, week = w.getCurrentWeekAndYear()

listWeek = w.weekdaterange(year, week)

menues = vecka(str(scrape('http://www.gladakocken.net/veckans-lunchmeny/', 'tr')))

for d in range(len(listWeek)):
    print(backend.updateMenu(year, week, listWeek[d], menues[d].getRatter()))
        
        