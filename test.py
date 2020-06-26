import smtplib, json, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

now = time.time()

email_config = json.loads(open('./EMAIL_CONFIG.json').read())

emails = [
    {
        'recip': 'marcus.brulls@gmail.com',
        'sub': 'Yeet',
        'cont': '<h1>Yaas queen succ my peen'
    },
    {
        'recip': 'vebbe90@gmail.com',
        'sub': 'Yeet',
        'cont': '<h1>Yaas queen succ my peen'
    }
]

def send_mail(recipient, subject, content):
    with smtplib.SMTP_SSL(email_config['host'], 465) as server:
        server.login(email_config['email'], email_config['password'])

        mail = MIMEMultipart('alternative')
        mail['Subject'] = subject
        mail['From'] = email_config['email']
        mail['To'] = recipient

        mail.attach(MIMEText(content, 'html'))

        server.sendmail(email_config['email'], recipient, mail.as_string())


print(time.time() - now)