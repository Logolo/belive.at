# -*- coding: utf-8 -*-

"""Live SocketIO notifications channel."""

import logging
logger = logging.getLogger(__name__)

from socketio import socketio_manage
from socketio.namespace import BaseNamespace as SocketIONamespace

from pyramid.response import Response
from pyramid.view import view_config

from ..hooks import get_redis_client

class LiveContext(SocketIONamespace):
    """"""
    
    def on_join(self, msg):
        """"""
        
        # Subscribe to redis notifications, listening for any events matching
        # ``*.user.canonical_id``.
        user = self.request.user
        pattern = '*:{0}'.format(user.canonical_id)
        redis = get_redis_client()
        subscriber = redis.pubsub()
        subscriber.psubscribe([pattern])
        logger.debug(u'Subscribing {0} to redis notifications'.format(user.username))
        for notification in subscriber.listen():
            parts = notification['channel'].split(':')
            name = parts[0]
            hashtag = parts[1]
            self.emit('notification', name, hashtag, notification['data'])
    


@view_config(route_name='live', renderer="json")
def live_view(request):
    socketio_manage(request.environ, {'/live': LiveContext}, request)
    return {}

