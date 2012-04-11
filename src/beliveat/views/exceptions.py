# -*- coding: utf-8 -*-

"""Exception views."""

import logging
logger = logging.getLogger(__name__)

from pyramid.exceptions import NotFound
#from pyramid.httpexceptions import HTTPBadRequest, HTTPForbidden

def not_found_view(context, request):
    return NotFound()

