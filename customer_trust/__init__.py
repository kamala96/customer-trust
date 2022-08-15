from flask import Flask, render_template, redirect, url_for
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
# RECAPTCHA_PUBLIC_KEY = "6LdcnnEhAAAAAALefXZ4W1B7R31Uf2_RySI4hsIF"
# RECAPTCHA_PRIVATE_KEY = "6LdcnnEhAAAAANgw9KtxUNFXrYIwB3RI_ooNp6TR"

# RECAPTCHA_PUBLIC_KEY = "6LeYIbsSAAAAACRPIllxA7wvXjIE411PfdB2gt2J"
# RECAPTCHA_PRIVATE_KEY = "6LeYIbsSAAAAAJezaIq3Ft_hSTo0YtyeFG-JgRtu"
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
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024  # 4MB max-limit.

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)

    from .models import User
    from werkzeug.security import generate_password_hash

    # Create a user to test with
    @app.before_first_request
    def create_user():
        try:
            db.create_all()
            default_super_user = User.query.filter_by(
                user_email='super@trust.com').first()

            default_user = User.query.filter_by(
                user_email='trust@trust.com').first()

            if default_super_user is None:
                super_admin = User(user_email='super@trust.com',
                                   user_password=generate_password_hash('123456', method='sha256'), is_admin=1)
                db.session.add(super_admin)
                db.session.commit()

            if default_user is None:
                user = User(user_email='trust@trust.com',
                            user_password=generate_password_hash('123456', method='sha256'))
                db.session.add(user)
                db.session.commit()
        except:
            pass

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

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    # Communicate with other files. This is all about to register blueprints
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .generator import generator as generator_blueprint
    app.register_blueprint(generator_blueprint)

    return app
