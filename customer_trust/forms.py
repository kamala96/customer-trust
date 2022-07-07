from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, PasswordField,
                     IntegerField, BooleanField, RadioField, SubmitField)
from wtforms.validators import InputRequired, Length, Email, Regexp


class CourseForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(),
                                             Length(min=10, max=100)])
    description = TextAreaField('Course Description',
                                validators=[InputRequired(),
                                            Length(max=200)])
    price = IntegerField('Price', validators=[InputRequired()])
    level = RadioField('Level',
                       choices=['Beginner', 'Intermediate', 'Advanced'],
                       validators=[InputRequired()])
    available = BooleanField('Available', default='checked')


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[InputRequired(message='Please enter your email address.'), Email(
        message='Please enter a valid email')], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=6, max=8), Regexp('(?=.*?[0-9])', message='Password should contain at least one digit')], render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')
    submit = SubmitField('Submit', render_kw={"value": "Ready To Go"})


class RegisterForm(FlaskForm):
    email = StringField('Email Address', validators=[InputRequired(message='Please enter your email address.'), Email(
        message='Please enter a valid email')], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=6, max=8), Regexp('(?=.*?[0-9])', message='Password should contain at least one digit')], render_kw={"placeholder": "Password"})
    submit = SubmitField('Submit', render_kw={"value": "Get Started"})
