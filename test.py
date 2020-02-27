import smtplib
from datetime import datetime
from time import time


config = open('./email.txt', 'r').readlines()

email       = config[0]
password    = config[1]

def gettime():
    timestamp   = time()
    t           = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return t

class emailerSSL:
    def __init__(self):
        self.errorlog   = open('errorlog.txt', 'a')
        self.server = smtplib.SMTP_SSL('protonmail.com', 465)
        self.server.login(email, password)

    def sendMail(self, recipient, subject, content):
        body = '\r\n'.join([
            'To: {}'.format(recipient),
            'From: {}'.format(email),
            'MIME-Version: 1.0',
            'Content-type: text/html',
            'Subject: {}'.format(subject),
            content
        ])

        try:
            self.server.sendmail(email, recipient, body)
            print('successfully sent mail')
        except Exception as e:
            print(e)
            self.errorlog.write('\n\n{}: {}'.format(gettime(), e))

server = emailerSSL()
server.sendMail('vebbe90@gmail.com', 'Hello World', '<h1>Yeet</h1>')
