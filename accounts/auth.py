from flask import Blueprint, render_template, request,redirect,url_for,flash
from . import db, mail,app
from .models import User
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,login_required,logout_user,current_user
from flask_mail import Message
from threading import Thread
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime


auth_bp=Blueprint('auth',__name__, static_folder="static", template_folder="templates")


@auth_bp.route('/login',methods=['GET','post'])
def login():
    if request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        
        user=User.query.filter_by(email=email).first()  # fetch data from User table by the email provided
        if user:   # if user is found
            if user.email_confirmed:  # if email is conirmed
                if check_password_hash(user.password, password): # check password
                    flash('logged in successfully',category='successful')
                    # once successful, call the login_user function
                    login_user(user,remember=True) # remember true avoids repetitive logins 
                    return redirect(url_for('views.home'))
                else:
                    flash('Incorrect username or password',category='error')
            else:
                flash('Your acount is not activated! Please open your email inbox and click activation link we sent to activate it', category='error')
        else:
            flash('User does not exist', category='error')
            
    return render_template('login.html',user=current_user) # current_user holds all info about the currently loggedin user 


@auth_bp.route('/logout')
@login_required  # makes sure we cannot access the route/page if user is not loggedin
def logout():
    logout_user()
    return redirect(url_for('auth.login'))



@auth_bp.route('/sign-up',methods=['GET','post'])
def sign_up():
    if request.method=='POST':
        email=request.form.get('email')
        first_name=request.form.get('firstName')
        password1=request.form.get('password1')
        password2=request.form.get('password2')
        
        #check if user is already exist.
        user=User.query.filter_by(email=email).first() 
        if user:
            flash('User already exists',category='error')
        # check vality of info provided
        elif len(email) < 4:
            flash('Email must be greater than 3 characters',category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character',category='error')
        elif password1 != password2:
            flash('Password dont match',category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters',category='error')
        else:
            new_user=User(email=email,first_name=first_name,password=generate_password_hash(password1, method='sha256'))  # instance to the User schema/table/class
            #add to database
            db.session.add(new_user)
            db.session.commit()
            
            send_confirm_email(new_user.email)   # send email confirmation. parameter can also be just email
            # after a successful user registration, flash successfully created.
            flash('Account created, kindly check your email to confirm email address',category='success')
            # a successful registration redirects user to a logged in page.so we track the logged in user
            # login_user(new_user,remember=True) # remember true avoids repetitive logins 
            # afterwards, redirect user to a loggedin page
            return redirect(url_for('auth.login'))
        
    return render_template("sign_up.html",user=current_user) # current_user holds all info about the currently loggedin user 

# this route is requested upon clicking a link via email
@app.route('/confirm/<token>')
def confirm_email(token):
    try:
        # verify email confirmation link. i.e, whether its authenticate and not expired
        confirm_serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
        email = confirm_serializer.loads(token, salt='email-confirmation-salt', max_age=86400)
    except:
        flash('The confirmation link is invalid or has expired.', category='error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(email=email).first()

    if user.email_confirmed:     # if email_confirmed is already True
        flash('Account already confirmed. Please login.', category='successful')
        return redirect(url_for('auth.login'))
    else:
        user.email_confirmed = True
        #user.email_confirmed_on = datetime.now()
        db.session.add(user)   # update the user with email_confirmed set to True and set confirmed date
        db.session.commit()
        flash('Thank you for confirming your email address!', category='successful')
        #upon successful confirmation be redirected to views.home (loged in)
    
    return redirect(url_for('views.home'))



# email confirmation functions
def send_async_email(msg):
    with app.app_context():
        mail.send(msg)


def send_email(subj, recip, html_bdy):
    msg = Message(subj, recipients=recip)
    msg.html = html_bdy
    tread = Thread(target=send_async_email, args=[msg])
    tread.start()


# this function will be called in the user_registration route.
#once the user_registration route is requsted(POST), the below function sends an email
#with a generated link (containing a token) to be clicked.
# once the link(containing a token) is clicked, the '/confirm/<token>' route will be called
def send_confirm_email(user_email):
    URL_conf_ts= URLSafeTimedSerializer(app.config['SECRET_KEY'])

    confirm_url = url_for('confirm_email', token=URL_conf_ts.dumps(user_email, salt='email-confirmation-salt'),_external=True)

    html = render_template('email_confm.html', confirm_url=confirm_url)

    send_email('Confirm Your Email Address', [user_email], html)

