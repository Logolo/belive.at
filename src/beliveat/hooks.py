# -*- coding: utf-8 -*-

"""Provides ``get_redis_client`` function."""

import json
import redis
from redis.connection import UnixDomainSocketConnection
redis_connection_pool = redis.ConnectionPool(path='/tmp/redis.sock', db=3,
        connection_class=UnixDomainSocketConnection)

from pyramid.httpexceptions import HTTPNotFound
from pyramid_assetgen import IAssetGenManifest

from .model import Hashtag
from .schema import Hashtag as ValidHashtag

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

def get_assetgen_manifest(request, interface_cls=IAssetGenManifest):
    """Get the manifest data registered for ``beliveat:assets``."""
    
    # XXX this is hardcoded and uses a private property.
    manifest = request.registry.getUtility(interface_cls, 'beliveat:assets/')
    return json.dumps(manifest._data)

