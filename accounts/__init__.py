from flask import Flask
from os import path
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail, Message

db = SQLAlchemy()   # instance to sqlalchamy ORM...db needs to be further initialized
mail = Mail()   # mail instance...mail needs to be further initialized
DB_NAME="database.db"

app=Flask(__name__)


def create_app():  
    
    app.config['SECRET_KEY']='thisismykey'  # for enceypting/siging session cookies

  #NOTE: WE NEEDED db or the app to be TO BE CREATED (initiated) BEFORE IMPORTING BLUEPRINTS      
    app.config['SQLALCHEMY_DATABASE_URI']= f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS_URI']= False
    #Email related Configuration values
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 465
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = 'gmail address here'
    app.config['MAIL_PASSWORD'] = 'gmail password here'   # to be removed
    app.config['MAIL_DEFAULT_SENDER'] = 'gmail address here'
    mail.init_app(app)
    db.init_app(app)

    
    from .views import views_bp
    from .auth import auth_bp
    
    
    # register blueprints 
    app.register_blueprint(views_bp, url_prefix='/')    # this first / is activated for a / route
    app.register_blueprint(auth_bp, url_prefix='/') 


    from .models import User, Note     # NOTE: The User and Note import should come before create_all function
    if not path.exists('accounts/' + DB_NAME):   # check whether database exists or not
        db.create_all(app=app)   # creates database and tables (imported from .models)
        print('Created Database')
    
    
    login_manager=LoginManager()  #object instance 
    login_manager.login_view='auth.login'  # where to be redirected when you are not loggedin
    login_manager.init_app(app)
    
    @login_manager.user_loader   # use this function to load user
    def load_user(id):
        return User.query.get(int(id))  # filters by primary key
    
    
    return app