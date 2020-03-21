import os
import bcrypt
import pymysql, pymysql.cursors
from base64 import b64encode, b64decode
import smtplib
import io
from datetime import datetime
from time import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json


dagar       = ['Måndag', 'Tisdag', 'Onsdag', 'Torsdag', 'Fredag']
cleaners    = ['<tr>', '</tr>', '<td>', '</td>']

def gettime():
    timestamp   = time()
    t           = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return t

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
    def __init__(self, email, name, password, verified):
        self.email      = email
        self.name       = name
        self.password   = password
        self.verified   = verified
        
class emailerSSL:
    def __init__(self, email, password):
        self.email = email
        self.errorlog   = open('errorlog.txt', 'a')
        self.server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        self.server.login(email, password)

    def sendmail(self, recipient, subject, content):
        mail = MIMEMultipart('alternative')
        mail['Subject'] = subject
        mail['From']    = self.email
        mail['To']      = recipient 
        
        mail.attach(MIMEText(content, 'html'))

        try:
            self.server.sendmail(self.email, recipient, mail.as_string())
            print('successfully sent mail')
        except Exception as e:
            print(e)
            self.errorlog.write('\n\n{}: {}'.format(gettime(), e))

class emailer:
    def __init__(self, serveremail):
        self.emailuser  = serveremail
        self.errorlog   = open('errorlog.txt', 'a')
        try:
            self.emailserver    = smtplib.SMTP('localhost')
        
        except Exception as e:
            print(e)
            self.errorlog.write('\n\n{}: {}'.format(gettime(), e))
            exit()
            
    
    def sendmail(self, recpient, subject, content):
        mail = 'From: From Person <{}>'.format(self.emailuser)
        mail+= '\nTo: To Person <{}>'.format(recpient)
        mail+= '\nMIME-Version: 1.0\nContent-type: text/html'
        mail+= '\nSubject: {}\n\n{}'.format(subject, content)
        try:
            self.emailserver.sendmail(self.emailuser, recpient, mail)
            return True
        
        except Exception as e:
            print(e)
            self.errorlog.write('\n\n{}: {}'.format(gettime(), e))
            return False

class basicusermanager(emailerSSL):
    def __init__(self, host, user, password, db, serveremail, emailpassword):
        super().__init__(serveremail, emailpassword)
        try:
            connection  = pymysql.connect(
                host, 
                user, 
                password, 
                db, 
                charset     = 'utf8mb4', 
                cursorclass = pymysql.cursors.DictCursor, 
                autocommit  = True)

            self.cur    = connection.cursor()

        except Exception as e:
            print(e)
            self.errorlog.write('\n\n{}: {}'.format(gettime(), e))


    #=======================================================================================
    # If function returns 1, an unverified user has been created with a verificationtoken added to the vertokens table.
    # If function returns 2, then the email adress has already been used and no new user has been created.
    # If function returns 3, then the name has already been used and no new user has been created.
    # If function returns 4, then both email and name has already been used and no new user has been created.
    def CreateNewUser(self, email, name, password):
        #B64 encoding is used to prevent SQL-injections
        email   = b64encode(email.encode('utf-8')).decode('utf-8')
        name    = b64encode(name.encode('utf-8')).decode('utf-8')
        try:
            self.cur.execute("SELECT email FROM users WHERE email = '{}';".format(email))
        except Exception as e:
            print(e)
            self.errorlog.write('\n\n{}: {}'.format(gettime(), e))
        
        #m is equal to zero if nobody has used the email before
        m       = len(self.cur.fetchall())
        
        try:
            self.cur.execute("SELECT name FROM users WHERE name = '{}';".format(name))
        except Exception as e:
            print(e)
            self.errorlog.write('\n\n{}: {}'.format(gettime(), e))

        #n is... well I think you get the idea
        n       = len(self.cur.fetchall())
        
        if m == 0 and n == 0:
            newuser = user_class(email, name, hashAndSalt(password), 0)
            try:
                self.cur.execute("INSERT INTO users(email, name, password, verified) VALUES ('{}', '{}', '{}', {});".format(
                    newuser.email,
                    newuser.name,
                    newuser.password,
                    newuser.verified
                ))
            except Exception as e:
                print(e)
                self.errorlog.write('\n\n{}: {}'.format(gettime(), e))

            token = b64encode(os.urandom(16)).decode('utf-8')
            try:
                self.cur.execute("INSERT INTO vertokens VALUES ('{}', '{}');".format(email, token))
            except Exception as e:
                print(e)
                self.errorlog.write('\n\n{}: {}'.format(gettime(), e))
            
            return 1, token
        
        elif m > 0 and n == 0:
            return 2, 'None'
        
        elif n > 0 and m == 0:
            return 3, 'None'
        
        else:
            return 4, 'None'

    #=======================================================================================
    # If function returns 1, then the login initials are correct and the account is verified.
    # If function returns 2, then the password is incorrect.
    # If function returns 3, then the account is not verified
    # If function returns 4, then the account does not exist.
    def loginInitialsCompare(self, email, pwd):
        email = b64encode(email.encode('utf-8')).decode('utf-8')
        try:
            self.cur.execute("SELECT email, password, verified FROM users WHERE email = '{}';".format(email))
        except Exception as e:
            print(e)
            self.errorlog.write('\n\n{}: {}'.format(gettime(), e))
        
        data = self.cur.fetchone()

        if data['verified'] == 1:
            if checkPW(pwd, data['password']):
                return 1
            
            else:
                return 2

        elif data['verified'] == 0:
            return 3

        else:
            return 4 
    
    def verifyuser(self, email, submittedtoken):
        email = (b64encode(email.encode('utf-8'))).decode('utf-8')
        try:
            self.cur.execute("SELECT token FROM vertokens WHERE email = '{}'".format(email))
        except Exception as e:
            print(e)
            self.errorlog.write('\n\n{}: {}'.format(gettime(), e))

        actualtoken = self.cur.fetchone()['token']

        if submittedtoken == actualtoken:
            try:
                self.cur.execute("UPDATE users SET verified = 1 WHERE email = '{}'".format(email))
            except Exception as e:
                print(e)
                self.errorlog.write('\n\n{}: {}'.format(gettime(), e))
            
            return True
        
        else:
            return False
    
    def MakeLoginSession(self, email) -> str:
        email   = b64encode(email.encode('utf-8')).decode('utf-8')

        try:
            self.cur.execute("DELETE FROM loginsessions WHERE email = '{}';".format(email))
        except Exception as e:
                print(e)
                self.errorlog.write('\n\n{}: {}'.format(gettime(), e))
        
        secret  = b64encode(os.urandom(64)).decode('utf-8')

        try:
            self.cur.execute("INSERT INTO loginsessions VALUES ('{}', '{}');".format(email, secret))
        except Exception as e:
                print(e)
                self.errorlog.write('\n\n{}: {}'.format(gettime(), e))
        
        return secret
    
    def checkSession(self, email, secret):
        email = b64encode(email.encode('utf-8')).decode('utf-8')
        
        try:
            self.cur.execute("SELECT email, secret FROM loginsessions WHERE email = '{}';".format(email))
        except Exception as e:
                print(e)
                self.errorlog.write('\n\n{}: {}'.format(gettime(), e))
        
        data = self.cur.fetchone()
        if data:
            actualsecret = data['secret']
            if secret == actualsecret:
                return True

            else:
                return False 
        else:
            return False

    def logoutUser(self, email):
        email = b64encode(email.encode('utf-8')).decode('utf-8')

        try:
            self.cur.execute("DELETE FROM loginsessions WHERE email = '{}';")
        except Exception as e:
                print(e)
                self.errorlog.write('\n\n{}: {}'.format(gettime(), e))

    def checkuserexists(self, email):
        email = b64encode(email.encode('utf-8')).decode('utf-8')
        try:
            self.cur.execute("SELECT COUNT(*) FROM users WHERE email = '{}';".format(email))
        except Exception as e:
            print(e)
            self.errorlog.write('\n\n{}: {}'.format(gettime(), e))


        if self.cur.fetchone()['COUNT(*)'] > 0:
            return True
        else:
            return False

    def makepasswordresettoken(self, email):
        email   = b64encode(email.encode('utf-8')).decode('utf-8')
        secret  = b64encode(os.urandom(64)).decode('utf-8')

        try:
            self.cur.execute("DELETE FROM passwordreset WHERE email = '{}';".format(email))
            self.cur.execute("INSERT INTO passwordreset VALUES ('{}', '{}');".format(email, secret))
            return secret, True

        except Exception as e:
            print(e)
            self.errorlog.write('\n\n{}: {}'.format(gettime(), e))
            return 'None', False 

    def resetpassword(self, email, secret, newpassword):
        email = b64encode(email.encode('utf-8')).decode('utf-8')
        try:    
            self.cur.execute("SELECT email, secret FROM passwordreset WHERE email = '{}';".format(email))
            data = self.cur.fetchone()
        except Exception as e:
            print(e)
            self.errorlog.write('\n\n{}: {}'.format(gettime(), e))
            
        if secret == data['secret']:
            try:
                self.cur.execute("UPDATE users SET password = '{}' WHERE email = '{}';".format(hashAndSalt(newpassword), email))
                self.cur.execute("DELETE FROM passwordreset WHERE email = '{}';".format(email))
                return True
            
            except Exception as e:
                print(e)
                self.errorlog.write('\n\n{}: {}'.format(gettime(), e))
                return False
        
        else:
            return False

    def getOrders(self, email) -> list:
        email       = b64encode(email.encode('utf-8')).decode('utf-8')
        try:
            self.cur.execute('SELECT orders FROM users WHERE email="%s"' % email)
        except Exception as e:
            self.errorlog.write('\n\n%s: %s' % (gettime(), e))
            ret     = ['Internal server error']
            return ret
        
        data        = self.cur.fetchone()
        if data['orders']:
            ret     = data['orders']
            #print(ret)
            return json.loads(ret)
        
        else:
            ret     = []
            return ret

    def makepasswordresettoken(self, email):
        email   = b64encode(email.encode('utf-8')).decode('utf-8')
        secret  = b64encode(os.urandom(64)).decode('utf-8')

        try:
            self.cur.execute("DELETE FROM passwordreset WHERE email = '{}';".format(email))
            self.cur.execute("INSERT INTO passwordreset VALUES ('{}', '{}');".format(email, secret))
            return secret, True

        except Exception as e:
            print(e)
            self.errorlog.write('\n\n{}: {}'.format(gettime(), e))
            return 'None', False 
    
    def makeAdminToken(self, email) -> tuple:
        email   = b64encode(email.encode('utf-8')).decode('utf-8')
        secret  = b64encode(os.urandom(64)).decode('utf-8')

        try:
            self.cur.execute("DELETE FROM admintokens WHERE email = '%s';" % email)
            self.cur.execute("INSERT INTO admintokens VALUES ('%s', '%s');" % (email, secret))
            return secret, True

        except Exception as e:
            print(e)
            self.errorlog.write('\n\n{}: {}'.format(gettime(), e))
            return 'None', False 

    def becomeAdmin(self, email, secret) -> bool:
        email   = b64encode(email.encode('utf-8')).decode('utf-8')

        try:
            self.cur.execute('SELECT token FROM admintokens WHERE email = "%s"' % email)
        except Exception as e:
            self.errorlog.write('\n\n%s: %s' % (gettime(), e))
        
        data    = self.cur.fetchone()['token']
        if data:
            if secret == data:
                try:
                    self.cur.execute('UPDATE users SET admin = 1 WHERE email = %s' % email)
                    return True
                except Exception as e:
                    self.errorlog.write('\n\n%s: %s' % (gettime(), e))

            else:
                return False
        else:
            return False

    def isAdmin(self, email) -> bool:
        email   = b64encode(email.encode('utf-8')).decode('utf-8')
        try:
            self.cur.execute('SELECT admin FROM users WHERE email = %s' % email)
        except Exception as e:
            self.errorlog.write('\n\n%s' % e)
            return False

        data    = self.cur.fetchone()['admin']

        if data == 1:
            return True
        else:
            return False