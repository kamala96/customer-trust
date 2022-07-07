from traitlets import default
from . import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), unique=True)
    user_password = db.Column(db.String(100))
    is_admin = db.Column(db.Integer, default=0)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def get_id(self):
        '''
        login_user calls get_id on the user instance. UserMixin provides a get_id method 
        that returns the id attribute or raises an exception. You did not define an id 
        attribute, you named it (redundantly) user_id. Name your attribute id (preferably), 
        or override get_id to return user_id
        '''
        return (self.user_id)
