from model.api import api, db_conn, send_mail, render_template, jsonify, datetime
from flask import request
import schedule, datetime, json, threading, time
from base64 import b64decode
import schedule



class event_handler(api):
    def __init__(self):
        super().__init__()
        self.methods = self.ret_event_methods()
        self.refresh_schedule()

        with db_conn().cursor() as conn:
            conn.execute('SELECT * FROM events;')
            if conn.rowcount == 0:
                initial_events = json.loads(open('./EVENTS.json').read())
                for e in initial_events:
                    conn.execute('INSERT INTO events VALUES ("%s", "%s", "%s", "%s", true);' % (e['name'], e['method'], e['day'], e['time_of_execution']))
        
        
        @self.route('/event_handler', methods=['POST'])
        def handle_event():
            auth_code = self.retAUTHCODE(request.cookies.get('loginsession'))[1]
            changes = request.get_json()['changes']
            ret = {
                'code': auth_code,
                'results': []
            }
            if auth_code == 1:
                with db_conn().cursor() as conn:
                    conn.execute('SELECT * FROM events;')
                    
                    if conn.rowcount > 0:
                        for e in conn.fetchall():
                            
                            #try:
                            if e['name'] in changes:
                                
                                change          =   changes[e['name']]
                                change_enabled  =   bool(change['event_enabled'])
                                change_time     =   datetime.datetime.strptime(change['time_of_execution'], '%H:%M')
                                change_time     =   change_time.strftime('%H:%M')

                                conn.execute('UPDATE events SET event_enabled=%r, time_of_execution="%s" WHERE name="%s";' % (
                                    change_enabled, 
                                    change_time,
                                    e['name']
                                ))
                                if conn.rowcount > 0:
                                    ret['results'].append({
                                        'name': change,
                                        'result': 'success'
                                    })
                                else:
                                    ret['results'].append({
                                        'name': change,
                                        'result': 'failed'
                                    })
                                    
                        self.refresh_schedule()
            return jsonify(ret)


        @self.route('/get_events', methods=['GET'])
        def get_events():
            code = self.retAUTHCODE(request.cookies.get('loginsession'))[1]
            ret = {'code': code, 'msg': self.AUTHCODES[code]}
            if code == 1: 
                with db_conn().cursor() as conn:
                    conn.execute('SELECT * FROM events;')
                    ret['events'] = []

                    if conn.rowcount > 0:
                        for e in conn.fetchall():
                            ret['events'].append(e)
            
            return jsonify(ret)

        def run_schedule():
            while True:
                schedule.run_pending()
                time.sleep(1)

        schedule_thread = threading.Thread(target=run_schedule, args=())
        schedule_thread.daemon = True
        schedule_thread.start()


    def refresh_schedule(self):
        with db_conn().cursor() as conn:
            conn.execute('SELECT * FROM events;')
            schedule.clear()
            if conn.rowcount > 0:
                for e in conn.fetchall():
                    if e['day'] == 'any' and e['method'] != 'None' and e['event_enabled']:
                        if e['method'] in self.methods:
                            schedule.every().day.at(e['time_of_execution']).do(self.methods[e['method']], self)


    def ret_event_methods(self):
        methods = [send_mail]

        def order_notify(self):
            with self.app_context():
                with db_conn() as conn:
                    today = datetime.datetime.now().date().isoformat()
                    conn.execute(
                        'SELECT userid, email FROM users WHERE verified=1;')
                    if conn.rowcount > 0:
                        q_ret = conn.fetchall()

                        conn.execute(
                            'SELECT menu FROM menues WHERE day="%s";' % ('2020-06-25'))
                        if conn.rowcount > 0:
                            menu = json.loads(conn.fetchone()['menu'])

                            for i in range(len(menu)):
                                menu[i] = b64decode(
                                    menu[i].encode('utf-8')).decode('utf-8')

                            for u in q_ret:
                                email = b64decode(u['email'].encode(
                                    'utf-8')).decode('utf-8')
                                u_id = u['userid']

                                conn.execute(
                                    'SELECT foodorder FROM orders WHERE day="%s" AND userid=%i;' % ('2020-06-25', u_id))

                                if conn.rowcount > 0:
                                    orders = []
                                    for o in json.loads(conn.fetchone()['foodorder']):
                                        orders.append({
                                            'food': menu[o['item']],
                                            'amount': o['amount']
                                        })

                                    send_mail(email, 'Order Notification', render_template(
                                        'emails/ordernotification.html', orders=orders))
        methods.append(order_notify)

        ret = {}
        for method in methods:
            ret[method.__name__] = method
        
        return ret
    
    