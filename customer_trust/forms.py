from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import (StringField, TextAreaField, PasswordField,
                     IntegerField, BooleanField, SubmitField)
from wtforms.validators import InputRequired, Length, Email, Regexp


# class CourseForm(FlaskForm):
#     title = StringField('Title', validators=[InputRequired(),
#                                              Length(min=10, max=100)])
#     description = TextAreaField('Course Description',
#                                 validators=[InputRequired(),
#                                             Length(max=200)])
#     price = IntegerField('Price', validators=[InputRequired()])
#     level = RadioField('Level',
#                        choices=['Beginner', 'Intermediate', 'Advanced'],
#                        validators=[InputRequired()])
#     available = BooleanField('Available', default='checked')


class LoginForm(FlaskForm):
    email = StringField('Email Address', validators=[InputRequired(message='Please enter your email address.'), Email(
        message='Please enter a valid email')], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=6, max=8), Regexp('(?=.*?[0-9])', message='Password should contain at least one digit')], render_kw={"placeholder": "Password"})
    remember = BooleanField('Remember Me')
    # recaptcha = RecaptchaField()
    submit = SubmitField('Submit', render_kw={"value": "Ready To Go"})


class RegisterForm(FlaskForm):
    email = StringField('Email Address', validators=[InputRequired(message='Please enter your email address.'), Email(
        message='Please enter a valid email')], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=6, max=8), Regexp('(?=.*?[0-9])', message='Password should contain at least one digit')], render_kw={"placeholder": "Password"})
    # recaptcha = RecaptchaField()
    submit = SubmitField('Submit', render_kw={"value": "Get Started"})


class DeleteIDForm(FlaskForm):
    id = IntegerField('Entry ID', validators=[InputRequired(
        message="Make sure you have submitted a valid entry")])


class AddPlatformForm(FlaskForm):
    platform_name = StringField('Platform Name', validators=[InputRequired()])
    platform_description = TextAreaField(
        'Platform Descriptions', validators=[InputRequired(), Length(max=200)])
    submit = SubmitField('Submit')


class AddProductForm(FlaskForm):
    product_name = StringField('Product Name', validators=[InputRequired()])
    product_description = TextAreaField(
        'Product Descriptions', validators=[InputRequired(), Length(max=200)])
    submit = SubmitField('Submit')


class AddFactorForm(FlaskForm):
    factor_name = StringField('Factor Name', validators=[InputRequired()])
    factor_description = TextAreaField(
        'Factor Descriptions', validators=[InputRequired(), Length(max=200)])
    submit = SubmitField('Submit')


class ImportSentimentsForm(FlaskForm):
    document = FileField('Sentiments File', validators=[FileRequired(message='Please attach a file'), FileAllowed(
        upload_set=['xls', 'xlsx', 'csv'], message='Excel and CSV Documents only!')])
    submit = SubmitField('Submit', render_kw={"value": "Import Data"})


class GneratorForm(FlaskForm):
    product = IntegerField('Product', validators=[InputRequired(
        message="Make sure you have submitted a valid entry")])
    factor = IntegerField('Trust Factor', validators=[InputRequired(
        message="Make sure you have submitted a valid entry")])
