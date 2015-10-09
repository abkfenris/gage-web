"""
Fabfile to setup and deploy gage-web
"""
from fabric.api import cd, run, local, env, sudo, put, prompt, lcd, prefix
from fabric.contrib.console import confirm
from fabtools import require
import fabtools

# uses a file called fabhosts where servers can be defined but gitignored
# looks like
#
# from fabric.api import env
#
# def prod():
#   env.user = 'username'
#   env.hosts = ['server1', 'server2']
#
try:
    from fabhosts import (prod,   # noqa
                          WWW_DIR,
                          ENV_DIR,
                          USER,
                          GROUP,
                          DB,
                          DB_USER,
                          DB_PASSWORD,
                          GIT_DIR)
except ImportError:
    pass

LOCAL_APP_DIR = '.'
LOCAL_CONFIG_DIR = LOCAL_APP_DIR + '/server-config'


def apt_upgrade():
    """
    Run apt-get upgrade
    """
    require.deb.uptodate_index(max_age={'day': 1})
    sudo('apt-get upgrade')


def create_user():
    """
    Create a gage_www user for running gage-web
    """
    require.groups.group(GROUP)
    require.users.user(USER, group=GROUP, system=True)


def create_www_folder():
    """
    Folder for gage-web to run from
    """
    require.directory(WWW_DIR,
                      use_sudo=True,
                      owner=USER)


def create_venv():
    """
    Create virutalenv for gage-web
    """
    require.python.virtualenv(ENV_DIR,
                              use_sudo=True)


def install_system_requirements():
    """
    Install required system packages
    """
    require.deb.packages(['python',
                          'python-dev',
                          'python-pip',
                          'python-virtualenv',
                          'nginx',
                          'postgresql-9.4',
                          'postgresql-9.4-postgis-2.1',
                          'postgresql-server-dev-9.4',
                          'libpq-dev',
                          'git',
                          'gdal-bin',
                          'gfortran',
                          'python-gdal',
                          'python-numpy',
                          'python-scipy',
                          'python-pandas',
                          'libblas-dev',
                          'liblapack-dev',
                          'libgdal-dev',
                          'supervisor',
                          'redis-server',
                          'libxslt1.dev',
                          'libjpeg8-dev',
                          'libjpeg-dev',
                          'libfreetype6-dev',
                          'zlib1g-dev',
                          'libpng12-dev'])
    sudo('export CPLUS_INCLUDE_PATH=/usr/include/gdal')
    sudo('export C_INCLUDE_PATH=/usr/include/gdal')


def create_database():
    """
    Create database and setup postgis
    """
    output = sudo('psql -lqt | cut -d \| -f 1', user='postgres')
    if DB in output:
        print('{DB} database found!'.format(DB=DB))
    else:
        print('{DB} not found! Creating DB'.format(DB=DB))
        # require.postgres.user(DB_USER, password=DB_PASSWORD)
        sudo("""psql -c "CREATE USER '{DB_USER}' NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT LOGIN UNENCRYPTED PASSWORD '{DB_PASSWORD}';""".format(DB_USER=DB_USER, DB_PASSWORD=DB_PASSWORD),
             user='postgres')
        # require.postgres.database(DB, owner=DB_USER)
        sudo('createdb --owner {DB_USER} {DB}'.format(DB_USER=DB_USER, DB=DB),
             user='postgres')
        sudo('psql -d {DB} -c "CREATE EXTENSION postgis;"'.format(DB=DB),
             user='postgres')
        sudo('psql -d {DB} -c "CREATE EXTENSION postgis_topology;"'.format(DB=DB),
             user='postgres')


def configure_git():
    """
    1. Setup bare Git Repo
    2. Create post-recieve hook
    """
    require.directory(GIT_DIR, use_sudo=True)
    with cd(GIT_DIR):
        #sudo('mkdir gage-web.git')
        with cd('gage-web.git'):
            #sudo('git init --bare')
            with lcd(LOCAL_CONFIG_DIR):
                with cd('hooks'):
                    put('./post-receive', './', use_sudo=True)
                    sudo('chmod +x post-receive')
    #with lcd(LOCAL_APP_DIR):
    #    local(
    #        'git remote add production {user}@{server}:{GIT_DIR}/gage-web.git'
    #        .format(user=env.user, server=env.host_string, GIT_DIR=GIT_DIR))


def deploy():
    """
    Push current master to production and restart gunicorn
    """
    with lcd(LOCAL_APP_DIR):
        local('git push production')
        sudo('supervisorctl restart gage:*')


def install_requirements():
    """
    Install requirements into virtualenv
    """
    with fabtools.python.virtualenv(ENV_DIR):
        with cd(WWW_DIR):
            require.python.requirements('requirements.txt')


def install_config_files():
    """
    Put config files for gunicorn, supervisord, nginx
    """
    # host-export
    with cd(WWW_DIR + '/server-config'):
        require.file('host-export', source=LOCAL_CONFIG_DIR+'/host-export')
        sudo('chmod +x host-export')
    # gunicorn
    with cd('/home/www'):
        fabtools.files.upload_template(
            LOCAL_CONFIG_DIR + '/gunicorn-start-gage',
            '.',
            use_sudo=True,
            use_jinja=True,
            user=USER,
            context={
                'WWW_DIR': WWW_DIR,
                'ENV_DIR': ENV_DIR,
                'USER': USER,
                'GROUP': GROUP
            },
            chown=True),
        sudo('chmod +x gunicorn-start-gage')
    # supervisord
    with cd('/etc/supervisor/conf.d/'):
        require.file('gage-web.conf',
                     source=LOCAL_CONFIG_DIR+'/gage-web.conf',
                     use_sudo=True)
        require.directory('/home/www/logs/gage-web/')
        sudo('supervisorctl reread')
        sudo('supervisorctl update')
    # nginx
    with cd('/etc/nginx/sites-available'):
        require.file('gage-web',
                     source=LOCAL_CONFIG_DIR+'/gage-web',
                     use_sudo=True)
        sudo('ln -s /etc/nginx/sites-available/gage-web' +
             ' /etc/nginx/sites-enabled/gage-web')
        sudo('service nginx configtest')
        sudo('service nginx restart')


def upgrade_db_schema():
    """
    With manage.py setup database
    """
    with prefix('source {ENV_DIR}/bin/activate'.format(ENV_DIR=ENV_DIR)):
        with prefix('source {WWW_DIR}/server-config/host-export'.format(WWW_DIR=WWW_DIR)):
            with cd(WWW_DIR):
                sudo('python manage.py db upgrade')


def create_roles():
    """
    Create user and admin roles
    """
    with prefix('source {ENV_DIR}/bin/activate'.format(ENV_DIR=ENV_DIR)):
        with prefix('source {WWW_DIR}/server-config/host-export'.format(WWW_DIR=WWW_DIR)):
            with cd(WWW_DIR):
                sudo('python manage.py user create_role -n admin -d "Site Administrators"')
                sudo('python manage.py user create_role -n user -d Users')

def setup_celery():
    """
    Upload configs for celery, make sure redis is running
    """
    with cd('/home/www'):
        fabtools.files.upload_template(
            LOCAL_CONFIG_DIR + '/celery-start-gage',
            '.',
            use_sudo=True,
            use_jinja=True,
            user=USER,
            context={
                'WWW_DIR': WWW_DIR,
                'ENV_DIR': ENV_DIR,
                'USER': USER,
                'GROUP': GROUP
            },
            chown=True),
        sudo('chmod +x celery-start-gage')
        fabtools.files.upload_template(
            LOCAL_CONFIG_DIR + '/celery-start-beat-gage',
            '.',
            use_sudo=True,
            use_jinja=True,
            user=USER,
            context={
                'WWW_DIR': WWW_DIR,
                'ENV_DIR': ENV_DIR,
                'USER': USER,
                'GROUP': GROUP
            },
            chown=True),
        sudo('chmod +x celery-start-beat-gage')
        with cd('/etc/supervisor/conf.d/'):
            require.file('gage-web.conf',
                         source=LOCAL_CONFIG_DIR+'/gage-web.conf',
                         use_sudo=True)
            require.directory('/home/www/logs/gage-web/')
            sudo('supervisorctl reread')
            sudo('supervisorctl update')
            sudo('supervisorctl restart gage:*')


def gage_restart():
    """
    Cron script to restart the supervisorctl gage:gage-celery-beat hourly
    """
    fabtools.cron.add_task('restart-gage-beat', '@hourly', 'root', WWW_DIR+'/server-config/restart-gage.sh')



def bootstrap():
    """
    Setup all the things
    """
    create_user()
    create_www_folder()
    create_venv()
    install_system_requirements()
    # create_database()
    # configure_git()
    deploy()
    install_requirements()
    # Install ssl scripts
    install_config_files()
    upgrade_db_schema()
    create_roles()
