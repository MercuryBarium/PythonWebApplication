from flask import Flask
from model.matlista import basicusermanager


backend = basicusermanager('localhost', 'pythonhttp', 'qwerty123', 'matlista', 'notmyname@localhost.com')

#backend.sendmail('joe@localhost.com', 'Hello World', '<h1>Hello World!</h1>')
loginhtml = open('./public/login.html', 'r').read()
reghtml = open('./public/register.html', 'r').read()
indexhtml = open('./public/index.html', 'r').read()

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return indexhtml.format('yeet')

@app.route('/register')
def register():
    return reghtml.format('')

@app.route('/login')
def login():
    return loginhtml.format('')



app.run('0.0.0.0', 8089)