#!/usr/bin/env python
import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models import User, Region, River, Section, Gage, Sensor, Sample
from app.user_manager import user_manager

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Region=Region, River=River,
                Section=Section, Gage=Gage, Sensor=Sensor, Sample=Sample)
manager.add_command("shell", Shell(make_context=make_shell_context))

manager.add_command('db', MigrateCommand)

manager.add_command('user', user_manager)

# @manager.command
# def deploy():
#    """Run deployment tasks."""
#    from flask.ext.migrate import upgrade
#
#    # migrate database to latest revision
#    upgrade()


# http://flask.pocoo.org/snippets/117/ manager helper to list routes
# http://stackoverflow.com/questions/13317536/get-a-list-of-all-routes-defined-in-the-app
@manager.command
def list_routes():
    """
    Lists routes for app
    """
    import urllib

    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.unquote("{:50s} {:20s} {}".format(rule.endpoint,
                                                        methods,
                                                        rule))
        output.append(line)

    for line in sorted(output):
        print(line)


@manager.command
def test(coverage=False):
    """
    Run the unit tests.
    """
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def backup():
    """
    Backup database to Dropbox
    """
    import datetime
    from app import backup as backup_db
    filename = 'gage_web-{time}.tar'.format(
        time=datetime.datetime.utcnow().strftime('%Y%m%d-%H%M'))
    os.system("pg_dump -Ft {db} > {filename}".format(
        db=db.engine.url.database,
        filename=filename))
    print('Uploading {filename} to Dropbox'.format(filename=filename))
    print(backup_db.backup(filename))
    os.system("rm " + filename)


if __name__ == '__main__':
    manager.run()
