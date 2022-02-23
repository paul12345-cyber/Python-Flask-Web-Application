from flask_login import UserMixin
from sqlalchemy.sql import func
from . import db    # . represent the parent folder (i.e., accounts)

# create database mddel
class User(db.Model,UserMixin):  # inheretance to Model and UserMixin classes. Note:db.Model intriniscally creates an object (db) to the inhereted Model class
    # obviously the below attribute/columns are constructor instances from the inhereted class
    # UserMixin gives the opportunity to use authentication functions like, current_user, is_authenticated, etc
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(150),unique=True)
    password=db.Column(db.String(150))
    first_name=db.Column(db.String(150))
    #email_confirmation_sent_on=db.Column(db.DateTime(timezone=True))
    email_confirmed= db.Column(db.Boolean, default=False)
    #email_confirmed_on=db.Column(db.DateTime(timezone=True))
    notes=db.relationship('Note')

    
    
class Note(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    message=db.Column(db.String(10000))
    date=db.Column(db.DateTime(timezone=True),default=func.now())
    # foreign key for userID
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    



