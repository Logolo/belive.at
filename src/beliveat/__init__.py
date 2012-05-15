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

from pyramid_assetgen import AssetGenRequestMixin
from pyramid_beaker import session_factory_from_settings
from pyramid_simpleauth.hooks import get_roles
from pyramid_simpleauth.tree import UserRoot

from .hooks import get_assetgen_manifest, get_redis_client
from .model import Base, Root, StoryRoot, TweetRoot
from .views.exceptions import not_found_view

class CustomRequest(AssetGenRequestMixin, Request):
    pass


def main(global_config, **settings):
    """Call with settings to create and return a WSGI application."""
    
    # Initialise a configurator.
    config = Configurator(settings=settings, root_factory=Root)
    
    # Include packages.
    config.include('pyramid_assetgen')
    config.include('pyramid_beaker')
    config.include('pyramid_tm')
    config.include('pyramid_weblayer')
    config.include('pyramid_simpleauth')
    config.commit()
    config.include('pyramid_twitterauth')
    config.include('pyramid_basemodel')
    
    # Expose routes.
    g = dict(use_global_views=True)
    config.add_route('index', '')
    config.add_route('stories', 'stories/*traverse', factory=StoryRoot, **g)
    config.add_route('tweets', 'tweets/*traverse', factory=TweetRoot, **g)
    config.add_route('users', 'users/*traverse', factory=UserRoot, **g)
    config.add_route('live', 'socket.io/*remaining')
    config.add_static_view('socket.io/lib', 'intr:static')
    
    # Expose ``/static``, cached for two weeks and make the assetgen manifest
    # available as ``request.assets``.
    config.add_static_view('static', 'beliveat:assets', cache_max_age=1209600)
    config.add_assetgen_manifest('beliveat:assets')
    config.set_request_property(get_assetgen_manifest, 'assets', reify=True)
    config.set_request_property(get_redis_client, 'redis', reify=True)
    config.set_request_factory(CustomRequest)
    
    # Configure a custom 404 that first tries to append a slash to the URL.
    not_found = AppendSlashNotFoundViewFactory(not_found_view)
    config.add_view(not_found, context=NotFound, permission=PUBLIC)
    
    # Run a venusian scan to pick up the declerative configuration.
    config.scan('beliveat')
    
    # Return a configured WSGI application.
    return config.make_wsgi_app()

