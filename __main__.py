from flask import Flask
from model.matlista import basicusermanager


backend = basicusermanager('localhost', 'pythonhttp', 'qwerty123', 'matlista', 'notmyname@localhost.com')

backend.sendmail('joe@localhost.com', 'Hello World', '<h1>Hello World!</h1>')

'''app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return '<h1>Hello World</h1>'

app.run('0.0.0.0', 8089)'''