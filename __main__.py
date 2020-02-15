from flask import Flask, request, redirect
from model.matlista import basicusermanager

#https://www.youtube.com/watch?v=1oad8uzSVwk
backend = basicusermanager('localhost', 'pythonhttp', 'qwerty123', 'matlista', 'notmyname@localhost.com')

#backend.sendmail('joe@localhost.com', 'Hello World', '<h1>Hello World!</h1>')
loginhtml = open('./public/login.html', 'r').read()
reghtml = open('./public/register.html', 'r').read()
indexhtml = open('./public/index.html', 'r').read()
verifactionpage = open('./public/verificationpage.html', 'r').read()

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return indexhtml.format('yeet')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return reghtml.format('')
    
    if request.method == 'POST':
        useremail = request.form.get('email')
        username = request.form.get('name')
        pwd = request.form.get('password')

        created, token = backend.CreateNewUser(useremail, username, pwd)
        if created == 1:
            backend.sendmail(useremail, 'Verificationtoken', '<h1>{}</h1>'.format(token))
            return redirect('/verify?email={}'.format(useremail))
        
        elif created == 2:
            return reghtml.format('Email address is already in use.')
        
        elif created == 3:
            return reghtml.format('Name is already in use.')
        
        elif created == 4:
            return reghtml.format('The entered name and email is already in use.')


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    if request.method == 'GET':
        return verifactionpage.format(request.args.get('email'), '')
    
    elif request.method == 'POST':
        useremail = request.form.get('email')
        token = request.form.get('token')
        verified = backend.verifyuser(useremail, token)
        if verified:
            return redirect('/login')
        
        else:
            return verifactionpage.format(useremail, 'Wrong token or email.')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return loginhtml.format('')
    
    elif request.method == 'POST':
        pass



app.run('0.0.0.0', 8089)