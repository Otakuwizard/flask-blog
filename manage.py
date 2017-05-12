from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.models import User, Role, Post, Comment, Follow, Tag, Blog, UserLike
import os

app = create_app(os.environ.get('FLABY_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

COV = None
if os.environ.get('FLABY_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

def make_shell_context():
    return dict(User=User, Role=Role, Post=Post, Comment=Comment, Follow=Follow, Blog=Blog, Tag=Tag, UserLike=UserLike, db=db, app=app)
    
@manager.command
def test(coverage=False):
    ''' Run the unit test'''
    if coverage and not os.environ.get('FLABY_COVERAGE'):
        import sys
        os.environ['FLABY_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable]+sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary: ')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % basedir)
        COV.erase()
        
@manager.command
def deploy():
    '''Run deployment tasks'''
    from flask_migrate import upgrade
    from app.models import Role, User
    
    upgrade()
    
    Role.insert_roles()
    
    User.insert_self_follow()
    
        
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()