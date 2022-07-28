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


class Ecommerce_platforms(db.Model, UserMixin):
    platform_id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.String(100), unique=True, nullable=False)
    platform_slug = db.Column(db.String(100), unique=True, nullable=False)
    platform_desc = db.Column(db.Text)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def get_id(self):
        return (self.platform_id)

    def to_dict(self):
        url = '<a href="/api/platforms-data/delete/{{self.get_id()}}" class="btn btn-danger btn-delete btn-sm"><i class="fa fa-fw fa-trash-o"></i>Delete</a>'
        return {
            'platform_id': self.platform_id,
            'platform_name': self.platform_name,
            'platform_desc': self.platform_desc,
            'date_created': self.date_created.strftime('%Y-%m-%d'),
        }


class Ecommerce_products(db.Model, UserMixin):
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), unique=True, nullable=False)
    product_slug = db.Column(db.String(100), unique=True, nullable=False)
    product_desc = db.Column(db.Text)
    product_platform = db.Column(db.Text, default='_')
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def get_id(self):
        return (self.product_id)


class Trust_facors(db.Model, UserMixin):
    factor_id = db.Column(db.Integer, primary_key=True)
    factor_name = db.Column(db.String(100), unique=True, nullable=False)
    factor_slug = db.Column(db.String(100), unique=True, nullable=False)
    factor_desc = db.Column(db.Text)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)

    def get_id(self):
        return (self.factor_id)
