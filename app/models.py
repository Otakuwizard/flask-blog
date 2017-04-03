from . import db
from . import login_manager
from flask import current_app, request
import uuid, time, hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, UserMixin, AnonymousUserMixin
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from markdown import markdown
import bleach
from . import login_manager

def generate_id():
    return '%015d%s000' % (int(time.time()*1000), uuid.uuid4().hex)
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
  
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.String(64), primary_key=True, default=generate_id)
    name = db.Column(db.String(32), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
  
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(64), primary_key=True, default=generate_id)
    user_name = db.Column(db.String(32), index=True, unique=True)
    email = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    location = db.Column(db.String(32))
    about_me = db.Column(db.Text())
    confirmed = db.Column(db.Boolean, default=False)
    register_at = db.Column(db.DateTime(), default=datetime.utcnow)
    last_login = db.Column(db.DateTime(), default=datetime.utcnow)
    role_id = db.Column(db.String(64), db.ForeignKey('roles.id'))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def ping(self):
        self.last_login = datetime.utcnow()
        db.session.add(self)
        
    def generate_confirm_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        set = dict(confirm=self.id)
        return s.dumps(set)
        
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if not data.get('confirm') or data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True
        
    
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.String(64), primary_key=True, default=generate_id)
    body = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    author_id = db.Column(db.String(64), db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.String(64), primary_key=True, default=generate_id)
    body = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    auhtor_id = db.Column(db.String(64), db.ForeignKey('users.id'))
    post_id = db.Column(db.String(64), db.ForeignKey('posts.id'))