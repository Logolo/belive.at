# -*- coding: utf-8 -*-

"""Provides the ``main()`` WSGI application entry point."""

import logging
logger = logging.getLogger(__name__)

import sys

from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.config import Configurator
from pyramid.exceptions import NotFound
from pyramid.request import Request
from pyramid.security import NO_PERMISSION_REQUIRED as PUBLIC
from pyramid.view import AppendSlashNotFoundViewFactory

from pyramid_beaker import session_factory_from_settings
from pyramid_simpleauth.hooks import get_roles
from pyramid_simpleauth.tree import UserRoot

from .model import Root
from .view import not_found_view

def main(global_config, **settings):
    """Call with settings to create and return a WSGI application."""
    
    # Initialise a configurator.
    config = Configurator(settings=settings, root_factory=Root)
    
    # Include packages.
    config.include('pyramid_basemodel')
    config.include('pyramid_beaker')
    config.include('pyramid_simpleauth')
    config.include('pyramid_tm')
    config.include('pyramid_weblayer')
    
    # Expose routes.
    config.add_route('index', '')
    config.add_route('foo', 'foo')
    config.add_route('users', 'users/*traverse', factory=UserRoot,
                     use_global_views=True)
    
    # Configure a custom 404 that first tries to append a slash to the URL.
    not_found = AppendSlashNotFoundViewFactory(not_found_view)
    config.add_view(not_found, context=NotFound, permission=PUBLIC)
    
    # Run a venusian scan to pick up the declerative configuration.
    config.scan('beliveat')
    
    # Return a configured WSGI application.
    return config.make_wsgi_app()

