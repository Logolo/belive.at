# -*- coding: utf-8 -*-

"""Provides ``get_redis_client`` function."""

import redis
from redis.connection import UnixDomainSocketConnection
redis_connection_pool = redis.ConnectionPool(path='/tmp/redis.sock', db=3,
        connection_class=UnixDomainSocketConnection)

def get_redis_client(request=None, cls=redis.StrictRedis):
    """Returns a ``redis`` client.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_cls = Mock()
          >>> mock_cls.return_value = 'redis client'
      
      Returns a ``cls`` instance configured with ``redis_connection_pool``::
      
          >>> get_redis_client(None, cls=mock_cls)
          'redis client'
          >>> mock_cls.assert_called_with(connection_pool=redis_connection_pool)
      
    """
    
    return cls(connection_pool=redis_connection_pool)

