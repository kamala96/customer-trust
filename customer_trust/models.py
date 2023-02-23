from . import db
from flask_login import UserMixin
from datetime import datetime


class Request(db.Model):
    __tablename__ = "request"

    index = db.Column(db.Integer, primary_key=True, autoincrement=True)
    response_time = db.Column(db.Float)
    date = db.Column(db.DateTime)
    method = db.Column(db.String)
    size = db.Column(db.Integer)
    status_code = db.Column(db.Integer)
    path = db.Column(db.String)
    user_agent = db.Column(db.String)
    remote_address = db.Column(db.String)
    exception = db.Column(db.String)
    referrer = db.Column(db.String)
    browser = db.Column(db.String)
    platform = db.Column(db.String)
    mimetype = db.Column(db.String)


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String(100), unique=True)
    user_password = db.Column(db.String(100))
    is_admin = db.Column(db.Integer, default=0)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.now)

    def get_id(self):
        '''
        login_user calls get_id on the user instance. UserMixin provides a get_id method 
        that returns the id attribute or raises an exception. You did not define an id 
        attribute, you named it (redundantly) user_id. Name your attribute id (preferably), 
        or override get_id to return user_id
        '''
        return (self.user_id)

    def __repr__(self):
        return f'<User "{self.user_email}">'


class Ecommerce_platforms(db.Model, UserMixin):
    platform_id = db.Column(db.Integer, primary_key=True)
    platform_name = db.Column(db.String(100), unique=True, nullable=False)
    platform_slug = db.Column(db.String(100), unique=True, nullable=False)
    platform_desc = db.Column(db.Text)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.now)
    platform_sentiments = db.relationship(
        'Sentiments', cascade="all,delete", backref='platform', lazy=True)

    def get_id(self):
        return (self.platform_id)

    def __repr__(self):
        return f'<Platform "{self.platform_name}">'

    def to_dict(self):
        return {
            'platform_id': self.platform_id,
            'platform_name': self.platform_name,
            'platform_desc': self.platform_desc,
            'date_created': self.date_created.strftime('%d %B, %Y %H:%M:%S'),
        }

    def to_dict_select(self):
        return {
            'value': self.platform_id,
            'text': self.platform_name,
        }


class Ecommerce_products(db.Model, UserMixin):
    product_id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), unique=True, nullable=False)
    product_slug = db.Column(db.String(100), unique=True, nullable=False)
    product_desc = db.Column(db.Text)
    product_keywords = db.Column(db.Text)
    product_platform = db.Column(db.Text)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.now)
    product_sentiments = db.relationship(
        'Sentiments', cascade="all,delete", backref='product', lazy=True)

    def get_id(self):
        return (self.product_id)

    def __repr__(self):
        return f'<Product "{self.product_name}">'

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'product_slug': self.product_slug,
            'product_desc': self.product_desc,
            'product_keywords': self.product_keywords,
            'product_platform': self.product_platform,
            'date_created': self.date_created.strftime('%d %B, %Y %H:%M:%S'),
        }

    def to_dict_select(self):
        return {
            'value': self.product_id,
            'text': self.product_name,
        }


class Trust_factors(db.Model, UserMixin):
    factor_id = db.Column(db.Integer, primary_key=True)
    factor_name = db.Column(db.String(100), unique=True, nullable=False)
    factor_slug = db.Column(db.String(100), unique=True, nullable=False)
    factor_rating = db.Column(db.Integer)
    factor_desc = db.Column(db.Text)
    factor_keywords = db.Column(db.Text)
    factor_products = db.Column(db.Text)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.now)
    factor_sentiments = db.relationship(
        'Sentiments', cascade="all,delete", backref='factor', lazy=True)

    def get_id(self):
        return (self.factor_id)

    def __repr__(self):
        return f'<Trust Factor "{self.factor_name}">'

    def to_dict(self):
        return {
            'factor_id': self.factor_id,
            'factor_name': self.factor_name,
            'factor_slug': self.factor_slug,
            'factor_rating': self.factor_rating,
            'factor_desc': self.factor_desc,
            'factor_keywords': self.factor_keywords,
            'factor_products': self.factor_products,
            'date_created': self.date_created.strftime('%d %B, %Y %H:%M:%S'),
        }


class Sentiments(db.Model, UserMixin):
    sentiment_id = db.Column(db.Integer, primary_key=True)
    sentiment_text = db.Column(db.String(100), nullable=False)
    sentiment_score = db.Column(db.Integer, nullable=False)
    sentiment_factor = db.Column(db.Integer, db.ForeignKey(
        'trust_factors.factor_id'), nullable=False)
    sentiment_product = db.Column(db.Integer, db.ForeignKey(
        'ecommerce_products.product_id'), nullable=False)
    sentiment_platform = db.Column(db.Integer, db.ForeignKey(
        'ecommerce_platforms.platform_id'), nullable=False)
    date_created = db.Column(
        db.DateTime, nullable=False, default=datetime.now)

    def get_id(self):
        return (self.sentiment_id)

    def __repr__(self):
        return f'<Sentiment "{self.sentiment_text[:20]}...">'

    def to_dict(self):
        return {
            'sentiment_id': self.sentiment_id,
            'sentiment_text': f'"{self.sentiment_text[:5]}..."',
            'sentiment_score': self.sentiment_score,
            'sentiment_factor': self.sentiment_factor,
            'sentiment_product': self.sentiment_product,
            'sentiment_platform': self.sentiment_platform,
            'date_created': self.date_created.strftime('%d %B, %Y %H:%M:%S'),
        }
