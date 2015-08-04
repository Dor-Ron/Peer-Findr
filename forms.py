#!usr/bin/env python

from flask_wtf import Form
from wtforms import StringField, PasswordField, SelectField
from wtforms.validators import DataRequired, Regexp, ValidationError, Email, Length, EqualTo

from models import Classmate
from courses import FALL_CLASSES

def user_exists(form, field):
    '''check if user exists, if it does raise error'''
    if Classmate.select().where(Classmate.username == field.data).exists():
        raise ValidationError('User with that name already exists.')

def email_exists(form, field):
    '''check if email exists, if it does raise error'''
    if Classmate.select().where(Classmate.email == field.data).exists():
        raise ValidationError('User with that email already exists.')


class RegisterForm(Form):
    '''WTForm registration form'''
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name  = StringField('Last Name', validators=[DataRequired()])
    username   = StringField('Username', validators=[DataRequired(), Length(min=4,  max=18), Regexp(r'^[a-zA-Z0-9_]+$', message='Username should be alphanumeric, be 4-18  characters long, and may include underscores'), user_exists])
    password   = PasswordField('Password', validators=[DataRequired(), Length(min=4, max=18), EqualTo('password2', message='Passwords must match and be between 4-18 characters')])
    password2  = PasswordField('Confirm Password', validators=[DataRequired()])
    first      = SelectField('Math class', choices=FALL_CLASSES[0], validators=[DataRequired()])
    second     = SelectField('Science class', choices=FALL_CLASSES[1], validators=[DataRequired()])
    third      = SelectField('English class', choices=FALL_CLASSES[2], validators=[DataRequired()])
    fourth     = SelectField('Speech/enginering class', choices=FALL_CLASSES[3], validators=[DataRequired()])
    fifth      = SelectField('Free Elective',  choices=FALL_CLASSES[4], validators=[DataRequired()])
    sixth      = SelectField('Other Class code', choices=FALL_CLASSES[5], validators=[DataRequired()])
    

class LoginForm(Form):
    '''WTForm login form'''
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])