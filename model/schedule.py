from model.api import api, db_conn, send_mail, render_template, jsonify
from flask import request
import schedule, datetime, json
from base64 import b64decode
import schedule



class event_handler(api):
    def __init__(self):
        super().__init__()
        self.methods = self.ret_event_methods()

        with db_conn().cursor() as conn:
            conn.execute('SELECT * FROM events;')
            if conn.rowcount == 0:
                initial_events = json.loads(open('./EVENTS.json').read())
                for e in initial_events:
                    conn.execute('INSERT INTO events VALUES ("%s", "%s", "%s", "%s", true);' % (e['name'], e['method'], e['day'], e['time_of_execution']))
        
        
        @self.route('/event_handler', methods=['POST'])
        def handle_event():
            return 'hello world'

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
                            'SELECT menu FROM menues WHERE day="%s";' % (today))
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
                                    'SELECT foodorder FROM orders WHERE day="%s" AND userid=%i;' % (today, u_id))

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
    
    