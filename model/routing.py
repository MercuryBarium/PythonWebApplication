from model.schedule import event_handler, render_template, request, send_mail
from flask import redirect, make_response
from urllib.parse import quote

class getters(event_handler):
    def __init__(self):
        super().__init__()

        @self.route('/')
        #===============GET=HANDLERS=================
        @self.route('/index', methods=['GET'])
        def index():
            email, code = self.retAUTHCODE(request.cookies.get('loginsession'))
            if code == 0 or code == 1:
                return redirect('/dashboard')
            else:
                return render_template('index.html')

        @self.route('/register', methods=['GET'])
        def register():
            email, code = self.retAUTHCODE(request.cookies.get('loginsession'))
            if code == 0 or code == 1:
                return redirect('/dashboard')
            else:
                return render_template('register.html')

        @self.route('/dashboard', methods=['GET'])
        def dashboard():
            email, code = self.retAUTHCODE(request.cookies.get('loginsession'))
            if code == 0 or code == 1:
                return redirect('/dashboard/orderfood.html')
            else:
                return redirect('/index')

        @self.route('/dashboard/<url>')
        def subboard(url=None):
            email, code = self.retAUTHCODE(request.cookies.get('loginsession'))
            if code == 0 or code == 1:
                try: 
                    return render_template('app/%s' % url)
                except:
                    return render_template('404.html')
            else:
                return redirect('/index')

        @self.route('/admin/<url>')
        def admin(url=None):
            email, code = self.retAUTHCODE(request.cookies.get('loginsession'))
            if code == 1:
                try:
                    return render_template('admin/%s' % url)
                except:
                    return render_template('404.html')
            else:
                return redirect('/index')

        @self.route('/forgotpassword', methods=['GET'])
        def forgotpassword():
            email   = request.args.get('email')

            if email:
                return render_template('newpassword.html')
            else:
                return render_template('forgotpassword.html')

        @self.route('/verifyuser', methods=['GET'])
        def verifyuser():
            return render_template('verificationpage.html')

        @self.route('/logout', methods=['GET'])
        def logout():
            email, code = self.retAUTHCODE(request.cookies.get('loginsession'))
            if code == 0 or code == 1:
                self.logoutUser(email)
                return redirect('/index?success=You-successfully-logged-out')
            else:
                return redirect('/index')

        @self.route('/wait_for_verify', methods=['GET'])
        def wait_for_verify():
            return render_template('autoverify.html')
        #============================================

class posters(getters):
    def __init__(self):
        super().__init__()

        #===============POST=HANDLERS================
        @self.route('/signin', methods=['POST'])
        def signin():
            email   = request.form.get('email')
            password= request.form.get('password')
            loggedin= request.cookies.get('loginsession')
            if loggedin:
                loggedin    = loggedin.split('|')
                user        = loggedin[0]
                secret      = loggedin[1]
                if self.checkSession(user, secret):
                    return redirect('/index?signinerror=You-are-already-logged-in')
                
                elif email and password:
                    if self.checkuserexists(email):    
                        opCode  = self.loginInitialsCompare(email, password)
                        if opCode == 1:
                            secret = self.MakeLoginSession(email)
                            resp = make_response('<div><script>window.location = "/index"</script></div>')
                            resp.set_cookie('loginsession', value='%s|%s' % (email, secret))
                            return resp
                        elif opCode == 2 or 4:
                            return redirect('/index?signinerror=Invalid-login-credentials')
                        
                        elif opCode == 3:
                            return redirect('/index?signinerror=You-need-to-verify-your-account-befor-logging-in')
                    else:
                        return redirect('/index?signinerror=Invalid-login-credentials')
                else:
                    return redirect('/index?signinerror=Fill-out-both-fields')
            
            else:
                if email and password:
                    if self.checkuserexists(email):    
                        opCode  = self.loginInitialsCompare(email, password)
                        if opCode == 1:
                            secret = self.MakeLoginSession(email)
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

        @self.route('/resettoken', methods=['POST'])
        def resettoken():
            email   = request.form.get('email')
            if email and self.checkuserexists(email):
                token, created = self.makepasswordresettoken(email)
                if created:
                    send_mail(email, 'Food Truck: Password reset token', render_template('emails/password_reset_mail.html', email=email, token=quote(token)))
                    return redirect('/forgotpassword?success=A-reset-token-has-been-sent-to-your-email')
                else:
                    return '<h1>Internal Server Error</h1>'
            else:
                return redirect('/forgotpassword?tokenerror=Invalid-email')
            
        @self.route('/resetpassword', methods=['POST'])
        def resetpassword():
            email       = request.form.get('email')
            password    = request.form.get('password')
            confirmation= request.form.get('confirmation')
            token       = request.form.get('token')
            if email and password and confirmation and token:
                if self.checkuserexists(email):
                    if password == confirmation:
                        if self.resetpassword(email, token, password):
                            return redirect('/index?success=Successful-password-reset')
                        else:
                            return redirect('/forgotpassword?email=%s&reseterror=' % email)
                    else:
                        return redirect('/forgotpassword?email=%s&reseterror=Password-and-confirmation-must-match' % email)
                else:
                    return redirect('/forgotpassword?tokenerror=Invalid-email')
            else:
                return redirect('/forgotpassword?email=%s&reseterror=All-fields-must-be-filled-out' % email)

        @self.route('/signup', methods=['POST'])
        def signup():
            email       = request.form.get('email')
            name        = request.form.get('name')
            password    = request.form.get('password')
            confirmation= request.form.get('confirmation')    
            if email and name and password and confirmation:
                if password == confirmation:
                    code, token = self.CreateNewUser(email, name, password)
                    if code == 1:
                        send_mail(email, 'Food Truck: Verification Token', render_template('emails/verifyemail.html', email=email, token=quote(token)))
                        return redirect('/index?success=An-email-with-your-verification-token-has-been-sent')
                    elif code == 2:
                        return redirect('/register?signuperror=Email-address-is-already-in-use')
                    elif code == 3:
                        return redirect('/register?signuperror=Name-is-already-in-use')
                    else:
                        return redirect('/register?signuperror=Both-name-and-email-is-already-in-use')
                else:
                    return redirect('/register?signuperror=Password-and-confirmation-needs-to-match')
            else:
                return redirect('/register?signuperror=All-fields-needs-to-be-filled-out')

