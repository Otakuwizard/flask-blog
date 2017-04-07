from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, PasswordField, SubmitField, ValidationError
from wtforms.validators import Email, Length, Regexp, Required, EqualTo
from ..models import User
from flask_login import current_user

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Email(), Length(1, 64)])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep Signin')
    submit = SubmitField('Log In')
    
class RegisterForm(FlaskForm):
    email = StringField('*Email', validators=[Required(), Email(), Length(1, 64)])
    user_name = StringField('*Username', validators=[Required(), Length(1, 64), Regexp('^[A-Za-z0-9\.\_]*$', 0, 
                            'Username must have only lettersm, numbers, dots and underscores.')])
    password1 = PasswordField('*Password', validators=[Required(), EqualTo('password2', message='Password must be matched.'),
                                Regexp('^(?!^[0-9a-z]+$)(?!^[0-9A-Z]+$)(?!^[a-zA-Z]+$)[a-zA-Z0-9]{6,20}$', 0, 
                                'Password must have a combination from letters and numbers and the langth must be 6 to 20.')])
    password2 = PasswordField('*Reenter your password', validators=[Required()])
    name = StringField('Real name')
    location = StringField('From')
    submit = SubmitField('Register')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already in used.')
    
    def validate_user_name(self, field):
        if User.query.filter_by(user_name=field.data).first():
            raise ValidationError('Username already in used.')

class PasswordChangeForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[Required()])
    new_password = PasswordField('New Password', validators=[Required(), EqualTo('new_password2', message='Password must be matched.'),
                                Regexp('^(?!^[0-9a-z]+$)(?!^[0-9A-Z]+$)(?!^[a-zA-Z]+$)[a-zA-Z0-9]{6,20}$', 0, 
                                'Password must have a combination from letters and numbers and the langth must be 6 to 20.')]) 
    new_password2 = PasswordField('*Reenter your password', validators=[Required()])
    submit = SubmitField('Confirm')
    
    def validate_old_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('Invalid Password')
            
class EmailChangeForm(FlaskForm):
    email = StringField('New Email', validators=[Required(), Email(), Length(1, 64)])
    submit = SubmitField('Confirm')
    
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already in used.')
            
class PasswordResetEmailForm(FlaskForm):
    email = StringField('Your Login Email', validators=[Required(), Email(), Length(1, 64)])
    submit = SubmitField('Send Token')
    
class PasswordResetForm(FlaskForm):
    password = PasswordField('New Password', validators=[Required(), EqualTo('password2', message='Password must be matched.'),
                                Regexp('^(?!^[0-9a-z]+$)(?!^[0-9A-Z]+$)(?!^[a-zA-Z]+$)[a-zA-Z0-9]{6,20}$', 0, 
                                'Password must have a combination from letters and numbers and the langth must be 6 to 20.')])
    password2 = PasswordField('*Reenter your password', validators=[Required()])
    submit = SubmitField('Confirm')
    