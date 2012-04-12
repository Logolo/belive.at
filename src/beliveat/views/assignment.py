# -*- coding: utf-8 -*-

"""Assignment views"""

import logging
logger = logging.getLogger(__name__)

import json
import operator
from datetime import timedelta

from pyramid.view import view_config

from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from ..model import Assignment, Hashtag, save as save_to_db
from ..schema import CreateAssignment

@view_config(route_name='assignments', name="your", request_method='GET',
        xhr=True, renderer='json')
def your_assignments_view(request):
    """Get your assignments sorted by most recent."""
    
    query = Assignment.query.filter_by(author=request.user)
    query = query.order_by(Assignment.created).limit(25)
    return [item.__json__() for item in query.all()]


@view_config(route_name='assignments', name="popular", request_method='GET',
        xhr=True, renderer='json', http_cache=timedelta(minutes=5))
def popular_assignments_view(request):
    """Get assignments sorted by rating."""
    
    # Cache in redis for five minutes
    KEY = 'beliveat:popular_assignments'
    results_str = request.redis.get(KEY)
    if results_str:
        results = json.loads(results_str)
    else: # Get the latest 2500 assignments and rank them.  Note that we strip out
        # the assignments from the current user client side, so this function can
        # be cached, seeing how it's so ridiculously expensive.
        compare_function = operator.attrgetter('rank')
        query = Assignment.query.order_by(Assignment.created)
        latest_assignments = query.limit(2500).all()
        latest_assignments.sort(key=compare_function, reverse=True)
        # Return the 25 most popular.
        results = [item.__json__() for item in latest_assignments[:25]]
        results_str = json.dumps(results)
        request.redis.setex(KEY, 300, results_str)
    # Return the list of results.
    return results


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

