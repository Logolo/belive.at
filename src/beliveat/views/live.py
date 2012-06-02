# -*- coding: utf-8 -*-

"""Live SocketIO notifications channel."""

import logging
logger = logging.getLogger(__name__)

from socketio import socketio_manage
from socketio.namespace import BaseNamespace as SocketIONamespace

from pyramid.response import Response
from pyramid.view import view_config

from ..model import Session

class LiveContext(SocketIONamespace):
    """Note that ``self.request`` is actually a redis pubsub subscriber."""
    
    @property
    def redis_pubsub_subscriber(self):
        """This property makes it explicit that ``self.request`` is actually a
          redis pubsub subscriber.
        """
        
        return self.request
    
    def on_join(self, msg):
        """Emit notifications to the user."""
        
        for notification in self.redis_pubsub_subscriber.listen():
            parts = notification['channel'].split(':')
            name = parts[0]
            hashtag = parts[1]
            self.emit('notification', name, hashtag, notification['data'])
    


@view_config(route_name='live', renderer="json")
def live_view(request, session=None, manage_socket=None):
    """Query the database and *close the db connection* before going into the
      death by hung db connection land of web sockets.
    """
    
    # Test jig.
    if session is None:
        session = Session
    if manage_socket is None:
        manage_socket = socketio_manage
    
    # Get the pattern for any events matching ``*.user.canonical_id``.
    user = request.user
    pattern = '*:{0}'.format(user.canonical_id)
    
    # Subscribe to them.
    subscriber = request.redis.pubsub()
    subscriber.psubscribe([pattern])
    
    # Print debug message.
    logger.debug(u'Subscribing {0} to notifications'.format(user.username))
    
    # IMPORTANT! Close the db connection.
    session.remove()
    
    # Hand over to the socket.io machinery.  This blocks the thread "forever".
    manage_socket(request.environ, {'/live': LiveContext}, subscriber)
    
    # If the socket loop exits, return.
    return {}

