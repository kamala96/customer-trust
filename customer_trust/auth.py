from flask import Blueprint, flash, render_template, url_for, request, redirect
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from .forms import LoginForm, RegisterForm
from .models import User
from . import PORTAL_TITLE, db
from flask_wtf.csrf import CSRFProtect


csrf = CSRFProtect()

auth = Blueprint('auth', __name__)
# csrf.exempt(auth)


def check_if_user_is_admin():
    # check if user is allowed to
    # e.g. JWT Token, Flask Login etc.
    # ...
    allowed = current_user.is_authenticated and current_user.is_admin == 1
    if not allowed:
        return redirect(url_for("auth.login"))


@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    title = PORTAL_TITLE + ' - Register Page'
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.email.data).first()

        if user:
            flash(message='Email address already exists', category='warning')
            return redirect(url_for('auth.signup'))

        new_user = User(user_email=form.email.data, user_password=generate_password_hash(
            form.password.data, method='sha256'))
        db.session.add(new_user)
        db.session.commit()
        flash(message='Success registration, please login here!',  category='success')
        return redirect(url_for('auth.login'))
    return render_template('signup.html', title=title, form=form)


@auth.route('/login', methods=['GET', 'POST'])
# @csrf.exempt
def login():
    title = PORTAL_TITLE + ' - Login Page'

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(user_email=form.email.data).first()

        if not user or not check_password_hash(user.user_password, form.password.data):
            flash(message='Please check your login details and try again',
                  category='warning')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember.data)
        return redirect(url_for('main.index'))
    return render_template('login.html', title=title, form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
