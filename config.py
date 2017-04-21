import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '*****'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLABY_MAIL_SUBJECT_PREFIX = 'FLABY'
    FLABY_MAIL_SENDER = 'FLABY Admin <fzj890909@gmail.com>'
    FLABY_ADMIN = os.environ.get('FLABY_ADMIN')
    
    @staticmethod
    def init_app(app):
        pass
        
class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI')
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI')
    WTF_CSRF_ENABLED = False
    
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') 
    
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}