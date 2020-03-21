from flask import Flask, request, redirect, make_response, jsonify
from model.matlista import basicusermanager
from public.view import get_html

config = open('./email.txt', 'r').readlines()

email       = config[0]
password    = config[1]

backend = basicusermanager('localhost', 'pythonhttp', 'qwerty123', 'matlista', email, password)

app = Flask(__name__)

def retAUTHCODE(req):
    

@app.route('/')

#===============GET=HANDLERS=================
@app.route('/index', methods=['GET'])
def index():
    loginsession    = request.cookies.get('loginsession')

    if loginsession:
        loginsession    = loginsession.split('|')
        email           = loginsession[0]
        secret          = loginsession[1]

        if backend.checkSession(email, secret):
            return get_html('dashboard')
        
        else:
            return get_html('index')
    else:
        return get_html('index')

@app.route('/forgotpassword', methods=['GET'])
def forgotpassword():
    email   = request.args.get('email')

    if email:
        return get_html('newpassword')
    else:
        return get_html('forgotpassword')

@app.route('/verifyuser', methods=['GET'])
def verifyuser():
    return get_html('verificationpage')
#============================================



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
            if backend.checkuserexists(email):    
                opCode  = backend.loginInitialsCompare(email, password)
                if opCode == 1:
                    secret = backend.MakeLoginSession(email)
                    resp = make_response('<div><script>window.location = "/index"</script></div>')
                    resp.set_cookie('loginsession', value='%s|%s' % (email, secret))
                    return resp
                elif opCode == 2 or 4:
                    return redirect('/index?signinerror=Invalid-login-credentials')
                
                elif opCode == 3:
                    return redirect('/verifyuser?email=%s' % email)
            else:
                return redirect('/index?signinerror=Invalid-login-credentials')
        else:
            return redirect('/index?signinerror=Fill-out-both-fields')
    
    else:
        if email and password:
            if backend.checkuserexists(email):    
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
                return redirect('/index?signinerror=Invalid-login-credentials')
        else:
            return redirect('/index?signinerror=Fill-out-both-fields')

@app.route('/resettoken', methods=['POST'])
def resettoken():
    email   = request.form.get('email')
    if email and backend.checkuserexists(email):
        token, created = backend.makepasswordresettoken(email)
        if created:
            backend.sendmail(email, 'Food Truck: Password reset token', get_html('emailtemplate') % ('Password reset token:', token))
            return redirect('/forgotpassword?email=%s' % email)
        else:
            return '<h1>Internal Server Error</h1>'
    else:
        return redirect('/forgotpassword?tokenerror=Invalid-email')
    
@app.route('/resetpassword', methods=['POST'])
def resetpassword():
    email       = request.form.get('email')
    password    = request.form.get('password')
    confirmation= request.form.get('confirmation')
    token       = request.form.get('token')
    if email and password and confirmation and token:
        if backend.checkuserexists(email):
            if password == confirmation:
                if backend.resetpassword(email, token, password):
                    return redirect('/index?success=Successful-password-reset')
                else:
                    return redirect('/forgotpassword?email=%s&reseterror=' % email)
            else:
                return redirect('/forgotpassword?email=%s&reseterror=Password-and-confirmation-must-match' % email)
        else:
            return redirect('/forgotpassword?tokenerror=Invalid-email')
    else:
        return redirect('/forgotpassword?email=%s&reseterror=All-fields-must-be-filled-out' % email)

@app.route('/signup', methods=['POST'])
def signup():
    email       = request.form.get('email')
    name        = request.form.get('name')
    password    = request.form.get('password')
    confirmation= request.form.get('confirmation')    
    if email and name and password and confirmation:
        if password == confirmation:
            code, token = backend.CreateNewUser(email, name, password)
            if code == 1:
                backend.sendmail(email, 'Food Truck: Verification Token', get_html('emailtemplate') % ('Verification Token', token))
                return redirect('/verifyuser?email=%s' % email)
            elif code == 2:
                return redirect('/index?signuperror=Email-address-is-already-in-use')
            elif code == 3:
                return redirect('/index?signuperror=Name-is-already-in-use')
            else:
                return redirect('/index?signuperror=Both-name-and-email-is-already-in-use')
        else:
            return redirect('/index?signuperror=Password-and-confirmation-needs-to-match')
    else:
        return redirect('/index?signuperror=All-fields-needs-to-be-filled-out')

@app.route('/verify', methods=['POST'])
def verify():
    email   = request.form.get('email')
    token   = request.form.get('token')
    if email:
        if backend.checkuserexists(email):
            if backend.verifyuser(email, token):
                return redirect('/index?success=Success,-new-user-is-now-verified')
            else:
                return redirect('/verifyuser?email=%s&verificationerror=Token-is-invalid' % email)
        else:
            return redirect('/verifyuser?verificationerror=User-does-not-exist')
    else:
        return redirect('/verifyuser?verificationerror=No-email-specified')

#application/json
@app.route('/auth', methods=['POST'])
def auth():
    ret             = {}
    ret['isAdmin']  = False
    authcookie  = request.cookies.get('loginsession').split('|')
    email       = authcookie[0]
    secret      = authcookie[1]
    if email and secret:
        if backend.checkSession(email, secret):
            ret['auth_code'] = 'success'
            ret['orders']    = backend.getOrders(email)
            if backend.isAdmin(email):
                ret['isAdmin']  = True
            print(ret)
            return jsonify(ret)
        else:
            ret['auth_code']    = 'failed_to_authenticate'
            return jsonify(ret)
    else:
        ret['auth_code']    = 'no auth cookie'
        return jsonify(ret)

@app.route('/sendadmintoken', methods=['POST'])
def sendadmintoken():
    authcookie  = request.cookies.get('loginsession').split('|')
    email       = authcookie[0]
    secret      = authcookie[1]
    jsonINPUT   = request.json
    ret         = {'code': 'None'}
    
    if email and secret:
        if backend.checkSession(email, secret):
            if backend.isAdmin(email):
                if jsonINPUT['email']:
                    if backend.checkuserexists(jsonINPUT['email']):
                        secret, created = backend.makeAdminToken(jsonINPUT['email'])
                        if created:
                            backend.sendmail(jsonINPUT['email'], 'Admin Token', get_html('emailtemplate') % ('Admin Token', secret))
                            ret['code'] = 'Success'
                            return jsonify(ret)
                        else:
                            ret['code'] = 'internal server error'
                            return jsonify(ret)
                    else:   
                        ret['code'] = 'User does not exist'
                else:
                    ret['code'] = 'input error'
                    return jsonify(ret)
            else:
                ret['code'] = 'You are not admin'
                return jsonify(ret)
        else:
            ret['code'] = 'invalid auth_code'
            return jsonify(ret)
    else:
        ret['code'] = 'No auth cookie'
        return jsonify(ret)

@app.route('/becomeadmin', methods=['POST'])
def becomeadmin():
    authcookie  = request.cookies.get('loginsession').split('|')
    email       = authcookie[0]
    secret      = authcookie[0]
    admintoken  = request.json['admintoken']
    
    if email and secret:
        if backend.checkSession(email, secret):
            if backend.becomeAdmin(email, admintoken):
                return jsonify({'code':'Success'})
            else:
                return jsonify({'code':'Error'})
        else:
            return jsonify({'code':'Unauthenticated'})
    else:
        return jsonify({'code':''})
    
#============================================

app.run(debug=True, host='0.0.0.0', port=8089, ssl_context=('./cert.pem', './key.pem'))