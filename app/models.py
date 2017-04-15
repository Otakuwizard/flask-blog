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
import hashlib
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
    
class Follow(db.Model):
    __tablename__ = 'follows'
    id = db.Column(db.String(64), primary_key=True, default=generate_id)
    followed_id = db.Column(db.String(64), db.ForeignKey('users.id'))
    follower_id = db.Column(db.String(64), db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
  
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
                role = Role(id=generate_id(), name=r)
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
    avatar_hash = db.Column(db.String(32))
    followed = db.relationship('Follow', foreign_keys=[Follow.follower_id], backref=db.backref('follower', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], backref=db.backref('followed', lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    
    def __init__(self, **kw):
        super(User, self).__init__(**kw)
        if self.role is None:
            if self.email == current_app.config['FLABY_ADMIN']:
                self.role = Role.query.filter_by(permission=0xff).first()
            else:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        
    
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
        
    def generate_confirm_token(self, expiration=3600, **kw):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        set = dict(**kw)
        set['confirm'] = self.id
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
        self.email = data.get('email') if data.get('email') is not None else self.email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True
    
    def can(self, permission):
        return self.role is not None and (self.role.permission & permission) == permission
        
    def is_administrator(self):
        return self.can(0xff)
        
    def gravatar(self, size=100, default='identicon', rating='g'):
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)
    
    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed, randint
        import forgery_py
        
        seed()
        for i in range(count):
            user = User(id=generate_id(),
                        email=forgery_py.internet.email_address(),
                        user_name=forgery_py.internet.user_name(True),
                        password=forgery_py.lorem_ipsum.word(),
                        confirmed=True,
                        name=forgery_py.name.full_name(),
                        location=forgery_py.address.city(),
                        about_me=forgery_py.lorem_ipsum.sentence(),
                        register_at=forgery_py.date.date(True))
            db.session.add(user)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()
    
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(id=generate_id(),
                        follower=self,
                        followed=user)
            db.session.add(f)
            db.session.commit()
    
    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()
    
    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None
    
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None
    
    @property
    def followed_posts(self):
        return Post.query.join('Follow', Follow.followed_id==Post.author_id).filter(Follow.follower_id==self.id)
    
    @staticmethod
    def insert_self_follow():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()
    
class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.String(64), primary_key=True, default=generate_id)
    body = db.Column(db.Text())
    body_html = db.Column(db.Text())
    created_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    author_id = db.Column(db.String(64), db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='post', lazy='dynamic')
    
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul', 'h1', 'h2', 'h3', 'p']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))
    
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py
        
        seed()
        user_count = User.query.count()
        for i in range(count):
            user = User.query.offset(randint(0, user_count-1)).first()
            post = Post(id=generate_id(),
                        body=forgery_py.lorem_ipsum.sentences(randint(1, 5)),
                        author=user,
                        created_at=forgery_py.date.date(True))
            db.session.add(post)
            db.session.commit()
    
class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.String(64), primary_key=True, default=generate_id)
    body = db.Column(db.Text())
    body_html = db.Column(db.Text())
    disabled = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime(), default=datetime.utcnow)
    auhtor_id = db.Column(db.String(64), db.ForeignKey('users.id'))
    post_id = db.Column(db.String(64), db.ForeignKey('posts.id'))
    
    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i', 'strong']
        target.body_html = bleach.linkify(bleach.clean(markdown(value, output_format='html'), tags=allowed_tags, strip=True))
        
    @staticmethod
    def generate_fake(count=100):
        from random import seed, randint
        import forgery_py
        
        seed()
        user_count = User.query.count()
        post_count = Post.query.count()
        for i in range(count):
            user = User.query.offset(randint(0, user_count-1)).first()
            post = Post.query.offset(randint(0, post_count-1)).first()
            comment = Comment(id=generate_id(),
                            body=forgery_py.lorem_ipsum.sentence(),
                            author=user,
                            post=post,
                            created_at=forgery_py.date.date(True))
            db.session.add(comment)
            db.session.commit()
            

class AnonymousUser(AnonymousUserMixin):
    def can(self, permission):
        return False
    
    def is_administrator(self):
        return False
    
    
login_manager.anonymous_user = AnonymousUser
db.event.listen(Post.body, 'set', Post.on_changed_body)
db.event.listen(Comment.body, 'set', Comment.on_changed_body)