# -*- coding: utf-8 -*-

"""User views."""

import logging
logger = logging.getLogger(__name__)

from pyramid.view import view_config

from pyramid_simpleauth.interfaces import IUser

@view_config(context=IUser, renderer='beliveat:templates/user.mako')
def user_view(request):
    logger.warn(' USER VIEW ')
    return {}

