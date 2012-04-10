# -*- coding: utf-8 -*-

""""""

import logging

from pyramid.exceptions import NotFound
from pyramid.response import Response
from pyramid.security import NO_PERMISSION_REQUIRED as PUBLIC
from pyramid.view import view_config

from pyramid_simpleauth.model import User

from socketio import socketio_manage
from socketio.namespace import BaseNamespace

def not_found_view(context, request):
    return NotFound()


@view_config(route_name='index', permission=PUBLIC,
        renderer='beliveat:templates/index.mako')
def index_view(request):
    return {'world': 'world'}


@view_config(route_name='foo', renderer='beliveat:templates/foo.mako')
def foo_view(request):
    return {}


@view_config(context=User, renderer='beliveat:templates/user.mako')
def user_view(request):
    return {}


class LiveContext(BaseNamespace):

    def on_join(self, msg):
        logging.warn('\n\n\nSOCKET.IO JOIN: %s\n\n\n' % msg)

@view_config(route_name='socket_io')
def sockio_view(request):
    socketio_manage(request.environ, {'/live': LiveContext}, request)
    return Response('')
