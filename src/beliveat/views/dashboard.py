# -*- coding: utf-8 -*-

"""Dashboard views."""

import logging
logger = logging.getLogger(__name__)

from pyramid.view import view_config

@view_config(route_name='dashboard', renderer='beliveat:templates/dashboard.mako')
def dashboard_view(request):
    
    # a) your stuff
    # b) general rankings
    
    
    
    #get my promote offers that are active (time / status flag)
    #    get the reports
    #    get the assignment
    #        get the report offers
    
    
    # ^ get all your stuff and then client side remove assignments already pinned
    # to the top from the general stuff
    
    
    # Ranking the assignments
    
    # Cap the latest N items. => limit
    # Run through the rank function.
    # 
    
    return {}


@view_config(route_name='dashboard', renderer='json', xhr=True)
def dashboard_ajax_view(request):
    data = dashboard_view(request)
    return {} # data.__json__()

