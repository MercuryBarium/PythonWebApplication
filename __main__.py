from model.infogathering.webscraper import scrape
from model.matlista import vecka, dbconnector
import smtplib

database = dbconnector('localhost', 'pythonhttp', 'qwerty123', 'matlista')
database.CreateNewUser('peter.brulls@gmail.com', 'Peter Brülls', 'abcd')