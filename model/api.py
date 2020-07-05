from model.matlista import basicusermanager, json, b64decode, db_conn, send_mail, render_template, getCurrentWeekAndYear, inTime, skipAhead, weekdaterange
from flask import request, jsonify
import datetime

class api(basicusermanager):
    def __init__(self):
        super().__init__()

        #application/json
        @self.route('/auth', methods=['POST'])
        def auth():
            email, code = self.retAUTHCODE(request.cookies.get('loginsession'))
            ret     = {'code':code, 'msg': self.AUTHCODES[code]}
            return jsonify(ret)

        @self.route('/makeadmin', methods=['POST'])
        def makeadmin():
            email, code = self.retAUTHCODE(request.cookies.get('loginsession'))
            ret     = {'code':code, 'msg': self.AUTHCODES[code]}
            target  = request.get_json()['email']
            if code == 1:
                if self.checkuserexists(target):
                    if self.becomeAdmin(target):
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


        @self.route('/fetchmenues', methods=['POST'])
        def fetchmenus():
            email, code = self.retAUTHCODE(request.cookies.get('loginsession'))
            ret     = {'code': code, 'msg':  self.AUTHCODES[code]}
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

        @self.route('/updatemenu', methods=['POST'])
        def updatemenu():
            email, code     = self.retAUTHCODE(request.cookies.get('loginsession'))
            jsonDATA        = request.get_json()
            year        = jsonDATA['year']
            week        = jsonDATA['week']
            day         = jsonDATA['day']
            menu        = jsonDATA['menu']

            ret         = {'code': code, 'msg':  self.AUTHCODES[code]}
            if code == 1:
                
                if type(year) == int and type(week) == int and type(day) == int:
                    if 0 <= day <= 4:
                        if len(menu) == 0:
                            ret['opcode'] = 'Empty menu'
                            return jsonify(ret)
                        day     = weekdaterange(year, week)[day]
                        delta   = datetime.datetime.strptime(day, '%Y-%m-%d')
                        if int(datetime.datetime.today().strftime('%V')) < int(delta.strftime('%V')):
                            if self.updateMenu(year, week, day, menu):
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

        @self.route('/updateorder', methods=['POST'])
        def updateorder():
            email, code = self.retAUTHCODE(request.cookies.get('loginsession'))
            ret = {'code': code, 'msg':  self.AUTHCODES[code]}
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
                
                if year and week and day and order:
                    userID = self.getUID(email)
                    if inTime(day=day):
                        todayYear, todayWeek = getCurrentWeekAndYear()
                        if todayYear == year and todayWeek == week:
                            if self.orderFOOD(userID, year, week, day, order):
                                ret['opcode'] = 'Success'
                                return jsonify(ret)
                            else:
                                ret['opcode'] = 'Error'
                                return jsonify(ret)
                        else:
                            ret['opcode'] = 'Order must be due the same week'
                            return jsonify(ret)
                    else:
                        ret['opcode'] = 'You are too late'
                        return jsonify(ret)
                else:
                    ret['opcode'] = 'Improper input'
                    return jsonify(ret)
            else:
                ret['opcode'] = 'illegal'
                return jsonify(ret)


        @self.route('/removemenu', methods=['POST'])
        def removemenu(): 
            email, code = self.retAUTHCODE(request.cookies.get('loginsession'))
            data    = request.get_json()
            year, week  = skipAhead(int(data['weekskip']))
            date    = str(weekdaterange(year, week)[int(data['day'])])
            ret     = {'code':code}

            yearnow, weeknow = getCurrentWeekAndYear()
            if (code == 1):
                with db_conn().cursor() as conn:
                    thisCursor = conn
                    if yearnow <= yearnow and weeknow < week:
                        try:
                            thisCursor.execute('DELETE FROM menues WHERE year=%i AND weeknumber=%i AND day="%s";' % (year, week, date))
                            ret['msg']  = 'success'
                        except:
                            ret['msg']  = '500'
            else:
                ret['msg']  = 'Illegal action'
            
            return jsonify(ret)


        @self.route('/fetchorder', methods=['POST'])
        def fetchorder():
            email, code = self.retAUTHCODE(request.cookies.get('loginsession'))
            data = request.get_json()
            ret = {'code': code, 'msg':  self.AUTHCODES[code], 'orders': []}
            if code == 0 or code == 1:
                with db_conn().cursor() as conn:
                    thisCursor = conn
                    uid = self.getUID(email)
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
                    
        @self.route('/dailyreport', methods=['GET'])
        def dailyreport():
            email, code = self.retAUTHCODE(request.cookies.get('loginsession'))
            ret = {'code': code, 'msg':  self.AUTHCODES[code]}
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


        @self.route('/individualreports', methods=['POST'])
        def individualreports():
            email, code = self.retAUTHCODE(request.cookies.get('loginsession'))
            ret = {'code': code, 'msg':  self.AUTHCODES[code], 'individuals': []}
            if code == 1:
                data = request.get_json()
                date_from = datetime.datetime.strptime(data['date_from'], '%Y-%m-%d')
                date_end = datetime.datetime.strptime(data['date_end'], '%Y-%m-%d')
                with db_conn() as conn:
                    conn.execute('SELECT userid, name FROM users WHERE 1=1;')
                    if conn.rowcount > 0:
                        users = conn.fetchall()
                        for u in users:
                            total_units_ordered = 0
                            username = b64decode(u['name'].encode('utf-8')).decode('utf-8')
                            u_id = u['userid']

                            select_date = date_from
                            while select_date <= date_end:
                                conn.execute('SELECT foodorder FROM orders WHERE userid=%i AND day="%s";' % (u_id, select_date.date()))
                                if conn.rowcount > 0:
                                    d = json.loads(conn.fetchone()['foodorder'])
                                    for o in d:
                                        total_units_ordered += o['amount']
                                
                                select_date += datetime.timedelta(days=1)
                            
                            ret['individuals'].append({
                                'name': username,
                                'total': total_units_ordered
                            })
            return jsonify(ret)

        #============================================