import requests
from bs4 import BeautifulSoup

def scrape(addr, element):
    src = requests.get(addr)

    soup = BeautifulSoup(src.text, 'lxml')

    rows = soup.findAll(element)

    return rows

#print(str(scrape('http://www.gladakocken.net/veckans-lunchmeny/', 'tr')))