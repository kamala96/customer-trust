import os
from flask import Flask, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'You Must Login to Access This Page!'
login_manager.login_message_category = 'danger'
csrf = CSRFProtect()

PORTAL_TITLE = 'Trust Portal'
RECAPTCHA_PUBLIC_KEY = "6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J"
RECAPTCHA_PRIVATE_KEY = "6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu"
SECRET_KEY = 'e0d82a214b61563b4569986e0c304584aefa87334da2729e91b082f24fa929c6'
SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite'
UPLOAD_FOLDER = 'customer_trust/static'

# This is the first file that get called when a project is runned
# Very useful when you want to set-up features only once


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['PORTAL_TITLE'] = PORTAL_TITLE
    app.config['RECAPTCHA_PUBLIC_KEY'] = RECAPTCHA_PUBLIC_KEY
    app.config['RECAPTCHA_PRIVATE_KEY'] = RECAPTCHA_PRIVATE_KEY
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB max-limit.

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        """Check if user is logged-in on every page load."""
        if user_id is not None:
            return User.query.get(int(user_id))
        return None

    # @login_manager.unauthorized_handler
    # def unauthorized():
    #     """Redirect unauthorized users to Login page."""
    #     flash('You must be logged in to view that page.', category='info')
    #     return redirect(url_for('auth.login'))

    # Communicate with other files. This is all about to register blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # from .generate_model import generate_model as generate_model_blueprint
    # app.register_blueprint(generate_model_blueprint)

    # from .reporting import reporting as reporting_blueprint
    # app.register_blueprint(reporting_blueprint)

    return app
