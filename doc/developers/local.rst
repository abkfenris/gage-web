Local Development
=================

If you're running it locally for development, you'll need
`Postgres 9.4 <http://www.postgresql.org>`_ with `Postgis <http://postgis.net>`_
and `Redis <http://redis.io>`_ as the two major backends.

To setup an empty database, ``psql`` in, create it and add the postgres
extensions.

.. code-block:: bash

    $ psql -c "CREATE DATABASE gage-web;"
    $ psql -d gage-web -c "CREATE EXTENSION postgis;"
    $ pqsl -d gage-web -c "CREATE EXTENSION postgis_topology;"

Requirements
------------
I suggest developing with a virtual environment.
`virtualenvwrapper <http://virtualenvwrapper.readthedocs.org>`_ makes working
with virtual environments much easier.

Then you can install the requirements. There are additional requirements for
development.

If you poke around in ``requirements.txt`` and the ``requirements``
folder, you'll notice that the dependencies have been broken into seperate
files. This is so that production servers and testing doesn't need to install
everything.

Also `Travis CI <http://travis-ci.org>`_ will install some packages much faster
with `miniconda <http://conda.pydata.org/miniconda.html>`_ than with `pip`.

.. code-block:: bash

    $ pip install -r requirements/develop.txt

If you are using a virtual environment, the following all assumes that it is
active.


Environment Variables
---------------------
Once you have your database and redis setup, you'll need to set the environment
variables expected in ``config.py``.

If you are using a virtual environment, you can add the variables to the
``activate`` file in the ``env/bin``.


Initial Migration
-----------------
With your database created, and running, you can use the ``db`` functions in
``manage.py``

To get the database ready run:

.. code-block:: bash

    $ python manage.py db init

Then you can bring it to the latest version of the schema with:

.. code-block:: bash

    $ python manage.py db upgrade

See `flask-Migrate <http://flask-migrate.readthedocs.org>`_ for more information.

Working with Users and Roles
----------------------------

``manage.py`` is able to manage users and roles on the server.

Roles
^^^^^

Before a user can be assigned a role, the role must exist, so create one with
``python manage.py user create_role``

.. program:: create_role
.. option:: -n <name>, --name <name>

    Name of role

.. option:: -d <description>, --description <description>

    Description of role

For example, to create an admin role:

.. code-block:: bash

    $ python manage.py user create_role -n admin

    Role admin created successfully.

Right now only an ``admin`` role is defined on the site, but others will be
setup in the future.

Users
^^^^^

You can create a user without `Roles`_ existing, but it makes sense to have them
setup first. Once roles are setup ``python manage.py user create_user`` allows
you to create a new account based on an email address.

.. program:: create_user
.. option:: -u <name@server.com>, --user <name@server.com>

    User name

.. option:: -p <password>, --password <password>

    Password

.. option:: -a <y> or <active>, --active <y> or <active>

    Is the user activated and allowed to log in?

For example, to add and activate a user:

.. code-block:: bash

    $ python manage.py user create_user -u test@server.com -p password -y a

    User created sucessfully.
    {
        "active": true,
        "email": "test@server.com",
        "password": "****"
    }

To give a user a specific role ``python manage.py user add_role`` is used

.. program:: add_role
.. option:: -u <name@server.com> or --user <name@server.com>

    Email address for user that you wish to add the role too

.. option: --r <role> or --role <role>

    Name of role to add to the user

If we wanted the user that we just created to be an admin:

.. code-block:: bash

    $ python manage.py user add_role -u test@server.com -r admin
    Role 'admin' added to user 'test@server.com' successfully


Other user focused commands include ``activate_user`` and ``deactivate_user`` if
you didn't explicitly activate a user upon account creation, or someone has been
misbehaving.

.. program:: activate_user
.. option:: -u <name@server.com> or --user <name@server.com>

    Email address for the user that you wish to modify

``remove_role`` is to remove a role from a user

.. program:: remove_role
.. option:: -u <name@server.com> or --user <name@server.com>

    Email address for the user that you wish to remove the role from

.. option: --r <role> or --role <role>

    Name of role to remove from a user

Running Everything
------------------
Now that hopefully all the bits and pieces are in place, you'll need three
terminals to get the server going. Remote gages are managed by
`Celery tasks <http://celeryproject.org>`_ which will run in the first two.

The first will run the Celery workers.

.. code-block:: bash

    $ celery worker -A celery_worker.celery -l info

    [tasks]
        . app.tasks.remote.fetch_h2oline_sample
        . app.tasks.remote.fetch_usgs_level_samples_all
        . app.tasks.remote.fetch_usgs_level_samples_chunk
        . app.tasks.remote.fetch_usgs_other_sample
        . fetch_remote_samples

    [2015-07-21 16:03:14,734: INFO/MainProcess] Connected to redis://localhost:6379/1
    [2015-07-21 16:03:14,742: INFO/MainProcess] mingle: searching for neighbors
    [2015-07-21 16:03:15,753: INFO/MainProcess] mingle: all alone
    [2015-07-21 16:03:15,765: WARNING/MainProcess] celery@localhost ready.

The second will manage the periodic tasks.

.. code-block:: bash

    $ celery beat -A celery_worker.celery -l info

    celery beat v3.1.18 (Cipater) is starting.
    __    -    ... __   -        _
    Configuration ->
        . broker -> redis://localhost:6379/1
        . loader -> celery.loaders.app.AppLoader
        . scheduler -> celery.beat.PersistentScheduler
        . db -> celerybeat-schedule
        . logfile -> [stderr]@%INFO
        . maxinterval -> now (0s)
    [2015-07-21 16:04:29,520: INFO/MainProcess] beat: Starting...

The third will run the server itself.

.. code-block:: bash

    $ python manage.py runserver
    * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
    * Restarting with stat

Then you can go to http://127.0.0.1:5000/ (or whatever the last command showed),
and start creating things.
