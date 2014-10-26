import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'o4d?2EXxt9.62Qj;ghXm[{#voUmF#$7ExY8T^V8BRC8si8faA$'
	dropbox_app_key = os.environ.get('DROPBOX_APP_KEY')
	dropbox_app_secret = os.environ.get('DROPBOX_APP_SECRET')
	dropbox_app_token = os.environ.get('DROPBOX_APP_TOKEN')
	SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/gage_web'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	DEBUG = True
	
	@staticmethod
	def init_app(app):
		pass
	


class DevelopmentConfig(Config):
	DEBUG = True
	DATABASE = {
		'name': 'main.db',
		'engine': 'peewee.SqliteDatabase'
	}
	#SERVER_NAME = 'flows.ngrok.com'
	
	
class TestingConfig(Config):
	TESTING = True
	DATABASE = {
		'name': 'main.db',
		'engine': 'peewee.SqliteDatabase'
	}

class DockerLocalConfig(Config):
	DEBUG = True
	DATABASE = {
		'name': 'db',
		'engine': 'peewee.PostgresqlDatabase',
		'user': 'postgres'
	}
	SERVER_NAME = "localhost"


class ProductionConfig(Config):
	DATABASE = {
		'name': os.environ.get('DATABASE_PATH') or 'data.db',
		'engine': 'peewee.SqliteDatabase'
	}
	SERVER_NAME = 'flows.alexkerney.com'

config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,
	
	'default': DevelopmentConfig
}