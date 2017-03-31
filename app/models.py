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

def generate_id():
    return '%015d%s000' % (int(time.time()*1000), uuid.uuid4().hex())
    
@login_manager.user_loader
def load_user(id):
    return User.query.get(id)
  
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.String(64), primary_key=True, default=generate_id)
    name = db.Column(db.String(32), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    users = db.relationship('User', backref='role', lazy='dynamic')
  
class User(db.Model):
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
    comments = db.realtionship('Comment', backref='author', lazy='dynamic')
    
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