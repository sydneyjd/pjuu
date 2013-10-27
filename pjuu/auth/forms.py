# 3rd party imports
from flask.ext.wtf import Form
from wtforms import PasswordField, TextField, ValidationError
from wtforms.validators import Email, EqualTo, Length, Regexp, Required

# Pjuu imports
from pjuu.users.models import User

# Package imports
from .backend import authenticate


class ForgotForm(Form):
    username = TextField('User name or E-Mail')


class LoginForm(Form):
    username = TextField('User name or E-Mail')
    password = PasswordField('Password')


class ResetForm(Form):
    password = PasswordField('Password', [
        EqualTo('password2', message='Passwords must match'),
        Length(min=6,
               message='Password must be atleast 6 characters long'),
        Required()])
    password2 = PasswordField('Confirm password')


class SignupForm(Form):
    username = TextField('User name', [
        Regexp(r'^[a-zA-Z0-9_]{3,16}$', message=('Username must be between 3 '
               'and 16 characters and can only contain '
               'lettrs, numbers and \'_\' characters.')),
        Required()])
    email = TextField('E-mail address', [Email(), Length(max=254), Required()])
    password = PasswordField('Password', [
        EqualTo('password2', message='Passwords must match'),
        Length(min=6,
               message='Password must be atleast 6 characters long'),
        Required()])
    password2 = PasswordField('Confirm password')

    def validate_username(form, field):
        user = User.query.filter(User.username.ilike(field.data)).first()
        if user is not None:
            raise ValidationError('User name already in use')

    def validate_email(form, field):
        user = User.query.filter(User.email.ilike(field.data)).first()
        if user is not None:
            raise ValidationError('E-mail address already in use')
