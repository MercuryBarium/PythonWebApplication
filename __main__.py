from flask import Flask, request, redirect, make_response
from model.matlista import basicusermanager

#https://www.youtube.com/watch?v=1oad8uzSVwk
backend = basicusermanager('localhost', 'pythonhttp', 'qwerty123', 'matlista', 'notmyname@localhost.com')

#backend.sendmail('joe@localhost.com', 'Hello World', '<h1>Hello World!</h1>')
loginhtml       = open('./public/login.html', 'r').read()
reghtml         = open('./public/register.html', 'r').read()
indexhtml       = open('./public/index.html', 'r').read()
verifactionpage = open('./public/verificationpage.html', 'r').read()


#============================================
maxlogintime = 7
#============================================
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return indexhtml.format('')

#========POST=HANDLERS=======================
@app.route('/registration', methods=['POST'])
def registration():
    useremail   = request.form.get('email')
    name        = request.form.get('name')
    password    = request.form.get('password')
    confirmation= request.form.get('confirmation')
    if useremail and name and password and confirmation:
        if useremail.count('@') != 1:
            return redirect('/register?error=Email-address-is-invalid')
        
        elif password != confirmation:
            return redirect('/register?error=Passwords-must-match')
        else:
            created, token = backend.CreateNewUser(useremail, name, password)
            
            if created == 1:
                backend.sendmail(useremail, 'Verificationtoken', '<h1>{}</h1>'.format(token))
                return redirect('/verification?email={}'.format(useremail))
            
            elif created == 2:
                return redirect('/register?error=Email-is-already-in-use')
            
            elif created == 3:
                return redirect('/register?error=Name-is-already-in-use')
            else:
                return redirect('/register?error=Both-email-and-name-is-already-in-use')
    else:
        return redirect('/register?error=All-fields-must-be-filled-out')

@app.route('/verify', methods=['POST'])
def verify():
    if request.form.get('email') and request.form.get('token'):
        if backend.verifyuser(request.form.get('email'), request.form.get('token')):
            return redirect('/login')
        else:
            return redirect('/verification?email={}?error=Invalid-token'.format(request.form.get('email')))
    
    else:
        return redirect('/verification?email={}?error=Invalid-form'.format(request.form.get('email')))

@app.route('/userlogin', methods=['POST'])
def userlogin():
    useremail   = request.form.get('email')
    password    = request.form.get('password')
    destination = request.form.get('destination')
    if useremail and password and destination:
        loginCode = backend.loginInitialsCompare(useremail, password)
        if loginCode == 1:
            secret  = backend.MakeLoginSession(useremail)
            resp    = make_response('<div><script>location.href = "{}"</script></div>'.format(destination)) 
            resp.set_cookie('loginsession', '{}|{}'.format(useremail, secret))
            return resp
        
        elif loginCode == 3:
            return redirect('/verification?email={}'.format(useremail))
        
        else:
            return redirect('/login?error=Invalid-login-credentials')

    else:
        return redirect('/login?error=All-field-are-required')

#============================================

#========GET=HANDLERS========================
@app.route('/register', methods=['GET'])
def register():
    if request.args.get('error'):
        return reghtml.format(request.args.get('error').replace('-', ' '))
    else:
        return reghtml.format('')

@app.route('/verification', methods=['GET'])
def verification():
    if request.args.get('error'):
        return verifactionpage.format(request.args.get('email'), request.args.get('error').replace('-',' '))
    
    else:
        return verifactionpage.format(request.args.get('email'), '')

@app.route('/login', methods=['GET'])
def login():
    error = request.args.get('error')
    if error:
        return loginhtml.format(error)
    
    else:
        return loginhtml.format('')



#============================================


app.run(debug=True, host='0.0.0.0', port=8089)