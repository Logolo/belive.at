# -*- coding: utf-8 -*-

""""""

from pyramid.exceptions import NotFound
from pyramid.security import NO_PERMISSION_REQUIRED as PUBLIC
from pyramid.view import view_config

from pyramid_simpleauth.model import User

def not_found_view(context, request):
    return NotFound()


@view_config(route_name='index', permission=PUBLIC,
        renderer='beliveat:templates/index.mako')
def index_view(request):
    return {}


@view_config(route_name='foo', renderer='beliveat:templates/foo.mako')
def foo_view(request):
    return {}



@view_config(context=User, renderer='beliveat:templates/user.mako')
def user_view(request):
    return {}

