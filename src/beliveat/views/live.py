# -*- coding: utf-8 -*-

"""Live SocketIO notifications channel."""

import logging
logger = logging.getLogger(__name__)

from socketio import socketio_manage
from socketio.namespace import BaseNamespace as SocketIONamespace

from pyramid.response import Response
from pyramid.view import view_config

class LiveContext(SocketIONamespace):
    """"""
    
    def on_join(self, msg):
        """"""
        
        logger.warn('\n\n\nSOCKET.IO JOIN: %s\n\n\n' % msg)
    


@view_config(route_name='live', renderer="json")
def live_view(request):
    socketio_manage(request.environ, {'/live': LiveContext}, request)
    return {}

