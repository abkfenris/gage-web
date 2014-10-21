#!/usr/bin/env python
import os





from app import create_app, db
from app.models import User, Region, River, Section, Gage, Sensor, Sample
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('GAGE_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

def make_shell_context():
	return dict(app=app, db=db, User=User, Region=Region, River=River, Section=Section, Gage=Gage, Sensor=Sensor, Sample=Sample)
manager.add_command("shell", Shell(make_context=make_shell_context)
manager.add_command('db', MigrateCommand)

@manager.command
def deploy():
	"""Run deployment tasks."""
	from flask.ext.migrate import upgrade
	
	# migrate database to latest revision
	upgrade()

if __name__ == '__main__':
	manager.run()