from flask import Flask, request, redirect, make_response
from model.matlista import basicusermanager
from public.view import get_html

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
    return get_html('index')


#===============POST=HANDLERS================
@app.route('/signin', methods=['POST'])
def signin():
    email   = request.form.get('email')
    password= request.form.get('password')
    loggedin= request.cookies.get('loginsession')
    if loggedin:
        loggedin    = loggedin.split('|')
        user        = loggedin[0]
        secret      = loggedin[1]
        if backend.checkSession(user, secret):
            return redirect('/index?signinerror=You-are-already-logged-in')
        
        elif email and password:
            opCode  = backend.loginInitialsCompare(email, password)
            if opCode == 1:
                secret = backend.MakeLoginSession(email)
                resp = make_response('<div><script>window.location = "/index"</script></div>')
                resp.set_cookie('loginsession', value='%s|%s' % (email, secret))
                return resp
            elif opCode == 2 or 4:
                return redirect('/index?signinerror=Ivalid-login-credentials')
            
            elif opCode == 3:
                return redirect('/verifyuser?email=%s' % email)
        else:
            return redirect('/index?signinerror=Fill-out-both-fields')
    
    else:
        if email and password:
            opCode  = backend.loginInitialsCompare(email, password)
            if opCode == 1:
                secret = backend.MakeLoginSession(email)
                resp = make_response('<div><script>window.location = "/index"</script></div>')
                resp.set_cookie('loginsession', value='%s|%s' % (email, secret))
                return resp
            elif opCode == 2 or 4:
                return redirect('/index?signinerror=Ivalid-login-credentials')
            
            elif opCode == 3:
                return redirect('/verifyuser?email=%s' % email)
        else:
            return redirect('/index?signinerror=Fill-out-both-fields')

@app.route('/signup', methods=['POST'])
def signup():
    return 'yaa'
#============================================


app.run(debug=True, host='0.0.0.0', port=8089, ssl_context=('./cert.pem', './key.pem'))