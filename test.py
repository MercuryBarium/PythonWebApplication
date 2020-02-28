import smtplib
from datetime import datetime
from time import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def gettime():
    timestamp   = time()
    t           = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    return t

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


