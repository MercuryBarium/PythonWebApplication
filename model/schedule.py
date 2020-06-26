from model.matlista import basicusermanager, db_conn, send_mail
import schedule, datetime, json
from base64 import b64decode
from flask import render_template

class event_handler(basicusermanager):
    def __init__(self):
        super().__init__()
        self.methods = self.ret_event_methods()

        with db_conn().cursor() as conn:
            conn.execute('SELECT * FROM events;')
            if conn.rowcount == 0:
                initial_events = json.loads(open('./EVENTS.json'))

        @self.route('/event_handler', methods=['POST'])
        def handle_event():
            pass
    

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
    
    