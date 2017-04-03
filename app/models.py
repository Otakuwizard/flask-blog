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
    
class Permission:
    FOLLOW = 0x01
    WRITE_ARTICLES = 0x02
    COMMENTS = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0xff
  
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.String(64), primary_key=True, default=generate_id)
    name = db.Column(db.String(32), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permission = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    @staticmethod
    def insert_roles():
        roles = {
            'administrator': [0xff, False],
            'moderator': [Permission.FOLLOW | Permission.WRITE_ARTICLES | Permission.COMMENTS | Permission.MODERATE_COMMENTS, False],
            'user': [Permission.FOLLOW | Permission.WRITE_ARTICLES | Permission.COMMENTS, True]
        }
        
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(id=generate_id(), name=)
                role.permission = roles[r][0]
                role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()
            
  
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
    
    def __init__(self, **kw):
        super(User, self).__init__(**kw)
        if self.role is None:
            if self.email == current_app.config['FLABY_ADMIN']:
                self.role = Role.query.filter_by(permission=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        
    
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
    
    def can(self, permission):
        return self.role is not None and (self.role.permission & permission) == permission
        
    def is_administrator(self):
        return self.can(0xff)
    
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