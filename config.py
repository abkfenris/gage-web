import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'o4d?2EXxt9.62Qj;ghXm[{#voUmF#$7ExY8T^V8BRC8si8faA$'
    dropbox_app_key = os.environ.get('DROPBOX_APP_KEY')
    dropbox_app_secret = os.environ.get('DROPBOX_APP_SECRET')
    dropbox_app_token = os.environ.get('DROPBOX_APP_TOKEN')
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAPBOX_MAP_ID = 'fenris.kdh92755'

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
    API_GAGES_PER_PAGE = 10
    SECRET_KEY = '1'
    CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://localhost/gage_web_testing'
    #SQLALCHEMY_ECHO = True


class DockerLocalConfig(Config):
    DEBUG = True
    SERVER_NAME = "localhost"


class ProductionConfig(Config):
    SERVER_NAME = 'flows.alexkerney.com'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
