# -*- coding: utf-8 -*-

"""Automated db, publish and deployment tasks."""

import os
import sys
import time

from ConfigParser import ConfigParser
from datetime import datetime

from fabric.api import run, sudo, hosts, local, cd, env, require, prompt, settings
from fabric.contrib.project import rsync_project
from fabric.contrib.console import confirm

# Setup the different environments for development, staging and live.

env.use_ssh_config = True

def _parse_ini(path, cls=ConfigParser):
    """Generate a ConfigObject instance for env.ini"""
    
    parser = cls()
    parser.read(path)
    return parser

def _ts():
    """Return the current second as a string like ``'1332786793'``."""
    
    t = time.mktime(datetime.utcnow().timetuple())
    return str(int(t))

def _shared():
    """Setup settings that are common to all the environments."""
    
    env.config = _parse_ini(env.config_file)
    env.version = _ts()


def development():
    """Setup the development environment using, e.g.:
      
          $ fab development my_task
      
    """
    
    env.config_file = 'etc/development.ini'
    _shared()

def staging():
    """Setup the staging environment using, e.g.:
      
          $ fab staging my_task
      
    """
    
    env.config_file = 'etc/staging.ini'
    env.hosts = ['beliveat']
    env.instance = 'staging'
    _shared()

def live():
    """Setup the live environment using, e.g.:
      
          $ fab live my_task
      
    """
    
    env.config_file = 'etc/live.ini'
    env.hosts = ['beliveat']
    env.instance = 'live'
    _shared()


# Database.

def db_create():
    """Create the postgresql db."""
    
    # Read the db info from the .ini config.
    db_user = env.config.get('app:main', 'db_user')
    db_name = env.config.get('app:main', 'db_name')
    db_password = env.config.get('app:main', 'db_password')
    
    # Create the user.
    cmd = "CREATE ROLE {0} WITH CREATEDB LOGIN PASSWORD '{1}';"
    sql = cmd.format(db_user, db_password)
    sudo('psql postgres -c "{}"'.format(sql), user='postgres')
    
    # Create the db.
    sudo('createdb -E UTF8 -T template0 -O {0} {1}'.format(db_user, db_name),
         user='postgres')

def db_up(target='head'):
    """Upgrade the db version to ``target``."""
    
    run('alembic -c {0} upgrade {1}'.format(env.config_file, target))

def db_down(target):
    """Downgrade the db version ``target``."""
    
    run('alembic -c {0} downgrade {1}'.format(env.config_file, target))

def db_stamp(target='head'):
    """Tell Alembic to create a new version table, and to stamp it with the most
      recent revision (i.e. head), as per http://bit.ly/GRhOS3
    """
    
    #run('alembic -c {0} stamp {1}'.format(env.config_file, target))
    raise NotImplementedError


# Publish

def test(package='beliveat'):
    """Run the tests."""
    
    local('nosetests --with-doctest --with-id {0}'.format(package), capture=False)

def publish(branch='master'):
    """Run tests locally and push ``branch`` to the git origin."""
    
    test()
    local('git push origin {0}'.format(branch))


# Deployment.

def test_on_server(package='beliveat'):
    """Run the tests."""
    
    run('nosetests --with-doctest --with-id {0}'.format(package), capture=False)

def install():
    """Install instance on the server.
      
      # mkdir
      # mkenv
      # git clone
      # source
      # develop
      
    """
    
    raise NotImplementedError

def deploy(branch='master', force_upgrade=False):
    """
      
      #* get the latest source code
      #* ... tbc.
      #* assetgen it up XXX patch assetgen to leave the existing files alone
      #* run tests on server
      #* ... tbc.
      
      # fab migrate staging|live [args]
      
      * show "temporarily down for maintenance" page
      * stop gunicorn
      * ... get the latest source parts of the deploy workflow ...
      * run migration
      * ... finish deploy workflow ...
      * clean up assetgen
      * start gunicorn
      * remove maintenance page
      
    """
    
    # Overwrite the private config.
    local('scp etc/{0}.ini beliveat:beliveat/instances/{0}/etc/{0}.ini'.format(env.instance))
    
    with cd('beliveat/instances/{0}'.format(env.instance)):
        
        # Forcefully terminate the pserve process.  XXX this should be graceful.
        with settings(warn_only=True):
            run('kill -TERM `cat pyramid.pid`')
        
        # Get the new source code.
        run('git pull origin {0}'.format(branch))
        
        # Re-develop the egg.
        run('../../env/bin/python2.6 setup.py develop -u')
        upgrade_flag = '-U' if force_upgrade else ''
        run('../../env/bin/python2.6 setup.py develop {0}'.format(upgrade_flag))
        
        # Restart the pserve process.
        run('../../env/bin/pserve etc/{}.ini --daemon'.format(env.instance))
    


# Admin helpers.

def new_user(username, email):
    """Add a new user."""
    
    raise NotImplementedError

def reset_password(username, password):
    """Reset a user's password."""
    
    raise NotImplementedError

