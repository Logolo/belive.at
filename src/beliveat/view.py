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

from .model import Assignment

def not_found_view(context, request):
    return NotFound()


@view_config(route_name='index', permission=PUBLIC,
        renderer='beliveat:templates/index.mako')
def index_view(request):
    return {'world': 'world'}


@view_config(route_name='dashboard', renderer='beliveat:templates/dashboard.mako')
def dashboard_view(request):
    
    # a) your stuff
    # b) general rankings
    
    
    
    get my promote offers that are active (time / status flag)
        get the reports
        get the assignment
            get the report offers
    
    
    # ^ get all your stuff and then client side remove assignments already pinned
    # to the top from the general stuff
    
    
    # Ranking the assignments
    
    # Cap the latest N items. => limit
    # Run through the rank function.
    # 
    
    return {}

@view_config(route_name='dashboard', renderer='json', is_xhr=True)
def dashboard_ajax_view(request):
    data = dashboard_view(request)
    return {} # data.__json__()




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





@view_config(route_name='assignments', name='create', renderer='json')
def create_assignment_view(request):
    """"""
    
    # schema.CreateAssignment
    
    # validate user input
    # create the Assignment
    
    # create promote offer (n.b.: remember if statement so don't show content
    # to it's originator to RT and auth increment the count if it's your own
    # content)
    
    return {} # assignment.__json__()

