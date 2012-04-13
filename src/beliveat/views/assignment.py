# -*- coding: utf-8 -*-

"""Assignment views"""

import logging
logger = logging.getLogger(__name__)

from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound
from pyramid.view import view_config

from pyramid_basemodel import save as save_to_db
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from ..model import Assignment, CoverOffer, PromoteOffer, Hashtag
from ..schema import CreateAssignment, AssignmentOffer

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


def create_offer(request, data, cls=CoverOffer, copy_count=False):
    """Shared logic to create a cover or a promote offer."""
    
    # Get the target assignment.
    hashtag = Hashtag.get_or_create(data['hashtag'])
    public_id = data['assignment']
    query = Assignment.query.filter_by(hashtag=hashtag, public_id=public_id)
    assignment = query.first()
    if not assignment:
        return HTTPNotFound()
    
    # Don't let a user create two offers for the same thing.
    if cls.query.filter_by(user=request.user, assignment=assignment).first():
        return HTTPBadRequest()
    
    # Create and save the offer.
    offer = cls(note=data['note'])
    offer.assignment = assignment
    offer.user = request.user
    #if copy_count: do the copy record count foo
    save_to_db(offer)
    return offer.__json__()

@view_config(route_name='assignments', name='cover', request_method='POST',
        xhr=True, renderer='json')
def cover_assignment_view(request, form_cls=Form):
    """Create a cover offer."""
    
    form = form_cls(request, schema=AssignmentOffer)
    if form.validate():
        return create_offer(request, form.data)
    request.response.status_int = 400
    return form.errors

@view_config(route_name='assignments', name='promote', request_method='POST',
        xhr=True, renderer='json')
def promote_assignment_view(request, form_cls=Form):
    """Create a promote offer."""
    
    form = form_cls(request, schema=AssignmentOffer)
    if form.validate():
        return create_offer(request, form.data, cls=PromoteOffer, copy_count=True)
    request.response.status_int = 400
    return form.errors

