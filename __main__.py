from flask import Flask, request, redirect, make_response
from model.matlista import basicusermanager
from public.view import mke_html

#https://www.youtube.com/watch?v=1oad8uzSVwk
config = open('./email.txt', 'r').readlines()

email       = config[0]
password    = config[1]

backend = basicusermanager('localhost', 'pythonhttp', 'qwerty123', 'matlista', email, password)

#============================================
maxlogintime = 7
#============================================
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return mke_html('index', ())




app.run(debug=True, host='0.0.0.0', port=8089)