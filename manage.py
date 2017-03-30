from flask_script import Manager, Shell
from falsk_migrate import Migrate, MigrateCommand
from app import create_app, db
import os

app = create_app(os.environ.get('FLABY_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

manager.add_command('db', MigrateCommand)

if __name == '__main__':
    manager.run()