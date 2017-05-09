from flask_wtf import FlaskForm
from wtforms import ValidationError, StringField, BooleanField, TextAreaField, SelectField, SubmitField
from flask_pagedown.fields import PageDownField
from wtforms.validators import Required, Email, Length, EqualTo, Regexp
from ..models import Role, User

class ProfileEditForm(FlaskForm):
    user_name = StringField('Username', validators=[Required(), Length(1, 64), Regexp('^[0-9a-zA-Z\_\.]+$', 0, 
                            'Usernames must hane only letters, numbers, dots or underscores.')])
    name = StringField('Your real name', validators=[Length(0, 64)])
    location = StringField('From', validators=[Length(0, 64)])
    about_me = TextAreaField('about me')
    submit = SubmitField('Confirm')
    
class ProfileEditAdminForm(FlaskForm):
    user_name = StringField('Username', validators=[Required(), Length(1, 64), Regexp('^[0-9a-zA-Z\_\.]+$', 0, 
                            'Usernames must hane only letters, numbers, dots or underscores.')])
    email = StringField('Email', validators=[Required(), Email(), Length(1, 64)])
    confirmed = BooleanField('Confirmed')
    name = StringField('Real Name', validators=[Length(0, 64)])
    location = StringField('From', validators=[Length(0, 64)])
    about_me = TextAreaField('About User')
    role = SelectField('Role')
    submit = SubmitField('Confirm')
    
    def __init__(self, user, *args, **kw):
        super(ProfileEditAdminForm, self).__init__(*args, **kw)
        self.user = user
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        
    def validate_user_name(self, field):
        if self.user.user_name != field.data and User.query.filter_by(user_name=field.data).first():
            raise ValidationError('username already in used')
    
    def validate_email(self, field):
        if self.user.email != field.data and User.query.filter_by(email=field.data).first():
            raise ValidationError('email already in used')
            
class PostCreateForm(FlaskForm):
    body = PageDownField('Share your mind.', validators=[Required()])
    submit = SubmitField('Submit')
    
class CommentCreateForm(FlaskForm):
    body = PageDownField('Your comment', validators=[Required()])
    submit = SubmitField('Submit')
    
class BlogCreateForm(FlaskForm):
    title = StringField('Title', validations=[Required(), Length(1, 128)])
    summary = StringField('Summary')
    body = PageDownField('Text', validations=[Required()])
    submit = SubmitField('Submit')
    