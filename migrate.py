from main import *
from flask_migrate import Migrate,init,upgrade,migrate,downgrade
from sys import argv
mig = Migrate(app,db)
with app.app_context():
    if argv[1] == 'upgrade':
        upgrade()
    elif argv[1] == 'init':
        init()
    elif argv[1] == 'migrate':
        migrate()
    elif argv[1] == 'downgrade':
        downgrade()
    else:
        print('Usage: python migrate.py [upgrade|migrate|downgrade]')