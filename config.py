import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '*****'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLABY_MAIL_SUBJECT_PREFIX = 'FLABY'
    FLABY_MAIL_SENDER = 'FLABY Admin <fzj890909@gmail.com>'
    FLABY_ADMIN = os.environ.get('FLABY_ADMIN')
    SSL_DISABLE = True
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    @staticmethod
    def init_app(app):
        pass
        
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URI')
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URI')
    WTF_CSRF_ENABLED = False
    
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI')
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost = (cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr = cls.FLABY_MAIL_SENDER,
            toaddrs = [cls.FLABY_ADMIN],
            subject = cls.FLABY_MAIL_SUBJECT_PREFIX + 'Application Error',
            credentials = credentials,
            secure = secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
        
class HerokuProductionConfig(ProductionConfig):
    SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))
    
    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)
        
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)
        
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler()
        file_handler.setLevel(logging.WARNING)
        app.logger.addhandler(file_handler)
        
    
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'heroku': HerokuProductionConfig,
    'default': DevelopmentConfig
}