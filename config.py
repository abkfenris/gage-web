import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'o4d?2EXxt9.62Qj;ghXm[{#voUmF#$7ExY8T^V8BRC8si8faA$'
    dropbox_app_key = os.environ.get('DROPBOX_APP_KEY')
    dropbox_app_secret = os.environ.get('DROPBOX_APP_SECRET')
    dropbox_app_token = os.environ.get('DROPBOX_APP_TOKEN')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAPBOX_MAP_ID = os.environ.get('MAPBOX_MAP_ID')
    MAPBOX_ACCESS_TOKEN = os.environ.get('MAPBOX_ACCESS_TOKEN')
    SECURITY_POST_LOGIN_VIEW = 'admin/'
    SECURITY_CHANGEABLE = True
    CELERY_BROKER_URL = 'redis://localhost:6379/1'
    SENTRY_USER_ATTRS = ['username', 'email']
    SENTRY_DSN = os.environ.get('SENTRY_DSN')
    CELERY_ACKS_LATE = True
    CELERYD_PREFETCH_MULTIPLIER = 1

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    API_GAGES_PER_PAGE = 2
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/gage_web'
    # SERVER_NAME = 'flows.ngrok.com'


class TestingConfig(Config):
    TESTING = True
    API_GAGES_PER_PAGE = 1
    SECRET_KEY = '1'  # noqa
    CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/gage_web_testing'
    CELERY_ALWAYS_EAGER = True
    # SQLALCHEMY_ECHO = True


class DockerLocalConfig(Config):
    DEBUG = True
    SERVER_NAME = "localhost"


class ProductionConfig(Config):
    SERVER_NAME = 'riverflo.ws'
    SECURITY_PASSWORD_HASH = 'bcrypt'  # noqa
    SECURITY_PASSWORD_SALT = (
        os.environ.get('SECRET_KEY') or
        'LMB#*42.)tHm4A;9Ce^hoPLN6C[m=3;2oTvK,vXA7EpMG4bg8x')
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('GAGE_DB') or
        'postgresql://localhost/gage-web')

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
