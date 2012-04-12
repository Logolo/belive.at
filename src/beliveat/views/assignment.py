# -*- coding: utf-8 -*-

"""Assignment views"""

import logging
logger = logging.getLogger(__name__)

from pyramid.view import view_config

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from ..model import Assignment, Hashtag, save as save_to_db
from ..schema import CreateAssignment

@view_config(route_name='assignments', request_method='GET', xhr=True,
        renderer='json')
def get_assignments_view(request):
    """Get assignments sorted by rating."""
    
    raise NotImplementedError


@view_config(route_name='assignments', name='create', request_method='POST',
        xhr=True, renderer='json')
def create_assignment_view(request, form_cls=Form):
    """Create an assignment."""
    
    form = form_cls(request, schema=CreateAssignment)
    if form.validate():
        d = form.data
        assignment = Assignment(title=d['title'], description=d['description'])
        assignment.hashtag = Hashtag.get_or_create(d['hashtag'])
        assignment.author = request.user
        save_to_db(assignment)
        # XXX create promote offer (n.b.: remember if statement so don't show
        # content to it's originator to RT and auth increment the count if
        # it's your own content)
        return assignment.__json__()
    request.response.status_int = 400
    return form.errors

