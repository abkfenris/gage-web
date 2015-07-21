fabfile.py
==========

`Fabric <http://www.fabfile.org>`_ is basically a makefile, except has server
management built in. Being able to run ``fab prod deploy`` to send your latest
modification to the server is sweet. It also is a great way to document common
tasks that you do when managing servers, without writing the whole process up in
Sphinx or elsewhere.

* `Hosts`_

Hosts
-----

Fabric seems to work best when you can login into a host with ssh keys, and
have sudo rights. So that the ``fabfile.py`` can be in source control, but
host information can be left out, the fabfile can get hosts from ``fabhosts.py``.

To create ``fabhost.py`` either copy and modify ``fabhost-example.py`` or write
along these lines:

.. code-block:: python

    from fabric.api import env

    def prod():
        env.user = 'user'
        env.hosts = [
            'host.com',
        ]

Then to run fabric with those hosts, just ``fab prod <command>``.

If you are awesome enough to have staging servers or other groups of server that
you will be commanding, define another command in ``fabhosts.py`` and modify
``fabfile.py`` import statement

.. code-block:: python

    try:
        from fabhost import prod, staging
    except ImportError:
        pass
