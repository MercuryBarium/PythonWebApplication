#https://pythontic.com/database/mysql/query%20a%20table
import os
import bcrypt
import pymysql
from base64 import b64encode, b64decode


dagar       = ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag']
cleaners    = ['<tr>', '</tr>', '<td>', '</td>']

class dag:
    def __init__(self, html):
        self.dag = 'Default'
        for d in dagar:
            if html.count(d):
                self.dag = d
                break

        self.ratter = []
        html = html.split('\n')
        for line in html:
            for x in range(1, 10):
                if line.count('{}:'.format(x)):
                    line = line.replace('</tr>, <tr><td>', '')
                    line = line.replace('</td>', '')
                    line = line.replace('&amp;', '&')
                    self.ratter.append(line)

    def getRatter(self):
        return self.ratter

    def getDag(self):
        return self.dag


def vecka(html):
    matlistor = html.split('<th')

    veckodagar = []

    for lista in matlistor:
        p = dag(lista)
        if not p.getDag() == 'Default':
            veckodagar.append(p)

    return veckodagar


def hashAndSalt(plaintext):
    return (bcrypt.hashpw(plaintext.encode('utf-8'), bcrypt.gensalt())).decode('utf-8')


def checkPW(plaintext, hashed):
    if bcrypt.checkpw(plaintext.encode('utf-8'), hashed.encode('utf-8')):
        return True
    else:
        return False


class user_class:
    def __init__(self, userid, email, name, password, verified):
        self.id         = userid
        self.email      = email
        self.name       = name
        self.password   = password
        self.verified   = verified
        

class dbconnector:
    def __init__(self, host, user, password, db):
        connection = pymysql.connect(host, user, password, db, charset='utf8mb4')
        self.cur = connection.cursor()

    def CreateNewUser(self, email, name, password):
        #B64 encoding is used to prevent SQL-injections
        email   = b64encode(email.encode('utf-8')).decode('utf-8')
        name    = b64encode(name.encode('utf-8')).decode('utf-8')
        self.cur.execute("SELECT  email FROM users WHERE email = '{}';".format(email))

        #m is equal to zero if nobody has used the email before
        m       = len(self.cur.fetchall())
        
        self.cur.execute("SELECT name FROM users WHERE name = '{}';".format(name))

        #n is... well I think you get the idea
        n       = len(self.cur.fetchall())
        
        if m == 0 and n == 0:
            self.cur.execute('SELECT COUNT(*) FROM users;')
            newid = str(self.cur.fetchone()[0] + 1)

            newuser = user_class(newid, email, name, hashAndSalt(password), 0)

            print('New unverified user has been created. ID:   {}'.format(newid))

            


database = dbconnector('localhost', 'pythonhttp', 'qwerty123', 'matlista')
database.CreateNewUser('something@email.com', 'joe', 'ABC')