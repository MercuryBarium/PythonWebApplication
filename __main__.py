from flask import Flask, request, redirect, make_response, jsonify, render_template
from model.matlista import basicusermanager, vecka, db_conn
from model.matlista import getCurrentWeekAndYear, skipAhead, weekdaterange, inTime
from base64 import b64decode
import pymysql
import pymysql.cursors
import datetime, json

config = open('./email.txt', 'r').readlines()

email       = config[0]
password    = config[1]

backend = basicusermanager('localhost', 'pythonhttp', 'qwerty123', 'matlista', email, password)


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
        return redirect('/dashboard')
    else:
        return render_template('index.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    email, code = retAUTHCODE(request.cookies.get('loginsession'))
    if code == 0 or code == 1:
        return redirect('/dashboard/orderfood.html')
    else:
        return redirect('/index')

@app.route('/dashboard/<url>')
def subboard(url=None):
    email, code = retAUTHCODE(request.cookies.get('loginsession'))
    if code == 0 or code == 1:
        try: 
            return render_template('app/%s' % url)
        except:
            return render_template('404.html')
    else:
        return redirect('/index')

@app.route('/admin/<url>')
def admin(url=None):
    email, code = retAUTHCODE(request.cookies.get('loginsession'))
    if code == 1:
        try:
            return render_template('admin/%s' % url)
        except:
            return render_template('404.html')
    else:
        return redirect('/index')

@app.route('/forgotpassword', methods=['GET'])
def forgotpassword():
    email   = request.args.get('email')

    if email:
        return render_template('newpassword.html')
    else:
        return render_template('forgotpassword.html')

@app.route('/verifyuser', methods=['GET'])
def verifyuser():
    return render_template('verificationpage.html')

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
            backend.sendmail(email, 'Food Truck: Password reset token', render_template('emailtemplate.html') % ('Password reset token:', token))
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
                backend.sendmail(email, 'Food Truck: Verification Token', render_template('emailtemplate.html') % ('Verification Token', token))
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


@app.route('/fetchmenues', methods=['POST'])
def fetchmenus():
    email, code = retAUTHCODE(request.cookies.get('loginsession'))
    ret     = {'code': code, 'msg': AUTHCODES[code]}
    week    = request.get_json()['week']
    if type(week) == int:
        if code == 1 or code == 0:
            with db_conn().cursor() as conn:
                thisCursor = conn
                ret['opcode']   = 'Success'
                if week == 0:
                    year, week  = getCurrentWeekAndYear()
                    listDates   = weekdaterange(year, week)
                    thisCursor.execute('SELECT day, menu FROM menues WHERE weeknumber = %i AND year = %i;' % (week, year))
                    ret['year']     = year
                    ret['week']     = week
                else:
                    year, week = skipAhead(week)
                    listDates = weekdaterange(year, week)
                    thisCursor.execute('SELECT day, menu FROM menues WHERE weeknumber = %i AND year = %i;' % (week, year))
                    ret['week']     = week
                    ret['year']     = year
                ret['menus']    = []

                
                for i in range(5):
                    ret['menus'].insert(i, {'day': listDates[len(ret['menus'])], 'menu': []})

                for m in thisCursor.fetchall():
                    m['menu'] = json.loads(m['menu'])
                    for i in range(len(m['menu'])):
                        m['menu'][i] = b64decode(m['menu'][i].encode('utf-8')).decode('utf-8')
                    
                    ret['menus'][datetime.date.weekday(datetime.datetime.strptime(m['day'], '%Y-%m-%d'))] = m

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
        with db_conn().cursor() as conn:
            thisCursor = conn
            if type(year) == int and type(week) == int and type(day) == int:
                if 0 <= day <= 4:
                    if len(menu) == 0:
                        ret['opcode'] = 'Empty menu'
                        return jsonify(ret)
                    day     = weekdaterange(year, week)[day]
                    delta   = datetime.datetime.strptime(day, '%Y-%m-%d')
                    #if int(datetime.datetime.today().strftime('%V')) < int(delta.strftime('%V')):
                    if backend.updateMenu(year, week, day, menu):
                        ret['opcode'] = 'success'
                        return jsonify(ret)
                    else:
                        ret['opcode'] = 'Bounced'
                        return jsonify(ret)
                    #else:
                    #   ret['opcode'] = 'Cannot update menues the same or after the week they are due'
                    #  return jsonify(ret)
                else:
                    ret['opcode'] = 'Improper Input'
                    return jsonify(ret)
            else:
                ret['opcode'] = 'Improper Input'
                return jsonify(ret)
    else:
        ret['opcode'] = 'Illegal'
        return jsonify(ret)

@app.route('/updateorder', methods=['POST'])
def updateorder():
    email, code = retAUTHCODE(request.cookies.get('loginsession'))
    ret = {'code': code, 'msg': AUTHCODES[code]}
    if code == 0 or code == 1:
        jsonINPUT   = request.get_json()
        year    = 0
        week    = 0
        day     = jsonINPUT['day']
        try:
            year    = int(datetime.date.strftime(datetime.datetime.strptime(day, '%Y-%m-%d'), '%Y'))
            week    = int(datetime.date.strftime(datetime.datetime.strptime(day, '%Y-%m-%d'), '%V'))
        except:
            ret['opcode'] = 'Date format issues'
            return jsonify(ret)
        
        order   = jsonINPUT['order']
        print(order)
        if year and week and day and order:
            userID = backend.getUID(email)
            #if inTime(day=day):
            todayYear, todayWeek = getCurrentWeekAndYear()
            if todayYear == year and todayWeek == week:
                if backend.orderFOOD(userID, year, week, day, order):
                    ret['opcode'] = 'Success'
                    return jsonify(ret)
                else:
                    ret['opcode'] = 'Error'
                    return jsonify(ret)
            else:
                ret['opcode'] = 'Order must be due the same week'
                return jsonify(ret)
            #else:
             #   ret['opcode'] = 'You are too late'
              #  return jsonify(ret)
        else:
            ret['opcode'] = 'Improper input'
            return jsonify(ret)
    else:
        ret['opcode'] = 'illegal'
        return jsonify(ret)


@app.route('/removemenu', methods=['POST'])
def removemenu(): 
    email, code = retAUTHCODE(request.cookies.get('loginsession'))
    data    = request.get_json()
    year, week  = skipAhead(int(data['weekskip']))
    date    = str(weekdaterange(year, week)[int(data['day'])])
    ret     = {'code':code}
    if (code == 1):
        with db_conn().cursor() as conn:
            thisCursor = conn
            try:
                thisCursor.execute('DELETE FROM menues WHERE year=%i AND weeknumber=%i AND day="%s";' % (year, week, date))
                ret['msg']  = 'success'
            except Exception as e:
                backend.logError(e)
                ret['msg']  = '500'
    else:
        ret['msg']  = 'Illegal action'
    
    return jsonify(ret)


@app.route('/fetchorder', methods=['POST'])
def fetchorder():
    email, code = retAUTHCODE(request.cookies.get('loginsession'))
    data = request.get_json()
    ret = {'code': code, 'msg': AUTHCODES[code], 'orders': []}
    if code == 0 or code == 1:
        with db_conn().cursor() as conn:
            thisCursor = conn
            uid = backend.getUID(email)
            startDate = datetime.datetime.strptime(data['startDate'], '%Y-%m-%d').date()
            endDate = datetime.datetime.strptime(data['endDate'], '%Y-%m-%d').date()

            if startDate <= endDate:
                while startDate <= endDate:
                
                    thisCursor.execute('SELECT year, weeknumber, day, foodorder FROM orders WHERE userid=%i AND day="%s";' % (uid, str(startDate)))
                    if thisCursor.rowcount > 0:
                        o = thisCursor.fetchone()
                        o['foodorder'] = json.loads(o['foodorder'])
                        thisCursor.execute('SELECT menu FROM menues WHERE day="%s";' % (str(startDate)))
                        o['menu'] = []

                        if thisCursor.rowcount > 0:
                            for m in json.loads(thisCursor.fetchone()['menu']):
                                m = b64decode(m.encode('utf-8')).decode('utf-8')
                                o['menu'].append(m)

                        ret['orders'].append(o)
                    startDate += datetime.timedelta(days=1)
    return jsonify(ret)
            
@app.route('/dailyreport', methods=['GET'])
def dailyreport():
    email, code = retAUTHCODE(request.cookies.get('loginsession'))
    ret = {'code': code, 'msg': AUTHCODES[code]}
    if code == 1:
        with db_conn() as conn:
            today = datetime.datetime.today().date()
            ret['orders'] = []
            conn.execute('SELECT menu FROM menues WHERE day="%s";' % (today.isoformat()))
            if conn.rowcount > 0:
                menus = json.loads(conn.fetchone()['menu'])
                for m in menus:
                    m = b64decode(m.encode('utf-8')).decode('utf-8')
                    ret['orders'].append({'food': m, 'amount': 0})

                conn.execute('SELECT foodorder FROM orders WHERE day="%s";' % (today.isoformat()))
                if conn.rowcount > 0:
                    individualOrders = conn.fetchall()
                    for i in individualOrders:
                        i = json.loads(i['foodorder'])
                        for o in i:
                            ret['orders'][o['item']]['amount'] += o['amount']
            
    return jsonify(ret)

#============================================

app.run(debug=True, host='0.0.0.0', port=8089)