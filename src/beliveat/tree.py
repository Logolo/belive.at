# -*- coding: utf-8 -*-

"""Provides Pyramid traversal factories that lookup context instances
  for the current request and specify who is allowed to access what.
"""

from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow, Deny
from pyramid.security import Authenticated, Everyone

class Root(object):
    """Root object of the application's resource tree."""
    
    __name__ = None
    
    __acl__ = [
        (Allow, 'r:admin', ALL_PERMISSIONS),
        (Allow, Authenticated, 'view'),
        (Deny, Everyone, ALL_PERMISSIONS),
    ]
    
    def __init__(self, request):
        self.request = request
    
    def __getitem__(self, key):
        raise KeyError
    

