# -*- coding: utf-8 -*-

"""Assignment views"""

import logging
logger = logging.getLogger(__name__)

from pyramid.view import view_config

from ..model import Assignment

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

