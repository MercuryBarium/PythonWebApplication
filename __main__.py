from flask import Flask, request, redirect, make_response, jsonify
from model.matlista import basicusermanager, vecka, wristwatch
from model.infogathering.webscraper import scrape
from public.view import get_html
from base64 import b64decode
import datetime, json

config = open('./email.txt', 'r').readlines()

email       = config[0]
password    = config[1]

backend = basicusermanager('localhost', 'pythonhttp', 'qwerty123', 'matlista', email, password)
serverTime = wristwatch()

app = Flask(__name__)

AUTHCODES   = [
    'User is authenticated',
    'Admin is authenticated',
    'Authentication failed',
    'User does not exist',
    'Improper auth cookie'
]

def retAUTHCODE(authcookie) -> tuple:
    if type(authcookie) == str and authcookie.count('|'):
        authcookie  = authcookie.split('|')
        email       = authcookie[0]
        secret      = authcookie[1]
        if backend.checkuserexists(email):
            if backend.checkSession(email, secret):
                if backend.isAdmin(email):
                    return email, 1
                else:
                    return email, 0
            else:
                return email, 2
        else:
            return email, 3
    else:
        return 'None', 4


@app.route('/')

#===============GET=HANDLERS=================
@app.route('/index', methods=['GET'])
def index():
    email, code = retAUTHCODE(request.cookies.get('loginsession'))
    if code == 0 or code == 1:
        return get_html('dashboard')
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

@app.route('/logout', methods=['GET'])
def logout():
    email, code = retAUTHCODE(request.cookies.get('loginsession'))
    if code == 0 or code == 1:
        backend.logoutUser(email)
        return redirect('/index?success=You-successfully-logged-out')
    else:
        return redirect('/index')
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
    email, code = retAUTHCODE(request.cookies.get('loginsession'))
    ret     = {'code':code, 'msg':AUTHCODES[code]}
    if code == 0 or code == 1:
        ret['orders']   = backend.getOrders(email)
        return jsonify(ret)
    else:
        return jsonify(ret)

@app.route('/makeadmin', methods=['POST'])
def makeadmin():
    email, code = retAUTHCODE(request.cookies.get('loginsession'))
    ret     = {'code':code, 'msg':AUTHCODES[code]}
    target  = request.get_json()['email']
    if code == 1:
        if backend.checkuserexists(target):
            if backend.becomeAdmin(target):
                ret['opcode']   = 0
                return jsonify(ret)
            else:
                ret['opcode']   = 1
                return jsonify(ret)
        else:
            ret['opcode']   = 2
            return jsonify(ret)
    else:
        ret['opcode']   = 3
        return jsonify(ret)

@app.route('/suggestmenu', methods=['POST'])
def suggestmenu():
    email, code = retAUTHCODE(request.cookies.get('loginsession'))
    ret         = {'code': code, 'msg': AUTHCODES[code]}
    if code == 1:
        ret['opcode']       = 'Success'
        ret['suggested']    = vecka(str(scrape('http://www.gladakocken.net/veckans-lunchmeny/', 'tr')))
        return jsonify(ret)
    else:
        ret['opcode']       = 'Illegal'
        return jsonify(ret)

@app.route('/fetchmenues', methods=['POST'])
def fetchmenus():
    email, code = retAUTHCODE(request.cookies.get('loginsession'))
    ret     = {'code': code, 'msg': AUTHCODES[code]}
    week    = request.get_json()['week']
    if type(week) == int:
        if code == 1 or code == 0:
            ret['opcode']   = 'Success'
            if week == 0:
                year, week  = serverTime.getCurrentWeekAndYear()
                listDates   = serverTime.weekdaterange(year, week)
                backend.cur.execute('SELECT day, menu FROM menues WHERE weeknumber = %i AND year = %i;' % (week, year))
                ret['year']     = year
                ret['week']     = week
            else:
                year, week = serverTime.skipAhead(week)
                listDates = serverTime.weekdaterange(year, week)
                backend.cur.execute('SELECT day, menu FROM menues WHERE weeknumber = %i AND year = %i;' % (week, year))
                ret['week']     = week
                ret['year']     = year
            ret['menus']    = []
            for m in backend.cur.fetchall():
                m['menu'] = json.loads(m['menu'])
                for i in range(len(m['menu'])):
                    m['menu'][i] = b64decode(m['menu'][i].encode('utf-8')).decode('utf-8')
                ret['menus'].append(m)
            
            while code == 1 and len(ret['menus']) != 5:
                ret['menus'].append({'day': listDates[len(ret['menus'])], 'menu': []})

            return jsonify(ret)
        else:
            ret['opcode']   = 'Illegal'
            return jsonify(ret)
    else:
        ret['opcode']   = 'Improper input'
        return jsonify(ret)

@app.route('/updatemenu', methods=['POST'])
def updatemenu():
    email, code     = retAUTHCODE(request.cookies.get('loginsession'))
    jsonDATA        = request.get_json()
    year        = jsonDATA['year']
    week        = jsonDATA['week']
    day         = jsonDATA['day']
    menu        = jsonDATA['menu']

    ret         = {'code': code, 'msg': AUTHCODES[code]}
    if code == 1:
        if type(year) == int and type(week) == int and type(day) == int:
            if 0 <= day <= 4:
                if len(menu) == 0:
                    ret['opcode'] = 'Empty menu'
                    return jsonify(ret)
                day     = serverTime.weekdaterange(year, week)[day]
                delta   = datetime.datetime.strptime(day, '%Y-%m-%d')
                if int(datetime.datetime.today().strftime('%V')) < int(delta.strftime('%V')):
                    if backend.updateMenu(year, week, day, menu):
                        ret['opcode'] = 'success'
                        return jsonify(ret)
                    else:
                        ret['opcode'] = 'Bounced'
                        return jsonify(ret)
                else:
                    ret['opcode'] = 'Cannot update menues the same or after the week they are due'
                    return jsonify(ret)
            else:
                ret['opcode'] = 'Improper Input'
                return jsonify(ret)
        else:
            ret['opcode'] = 'Improper Input'
            return jsonify(ret)
    else:
        ret['opcode'] = 'Illegal'
        return jsonify(ret)


#============================================

app.run(debug=True, host='0.0.0.0', port=8089, ssl_context=('./cert.pem', './key.pem'))