# -*- coding: utf-8 -*-

"""Dashboard views."""

import logging
logger = logging.getLogger(__name__)

import json
import operator

from datetime import timedelta
from pyramid.view import view_config
from pyramid_basemodel import Session, save as save_to_db

from ..model import Assignment, Hashtag
from ..model import CoverOffer, PromoteOffer
from ..model import Tweet
from ..model import get_one_week_ago

def get_your_cover_offers(request):
    """Get your coverage offers for the current #hashtag."""
    
    query = Session.query(CoverOffer)
    query = query.filter(CoverOffer.user==request.user)
    query = query.filter(Assignment.hashtag==request.hashtag)
    query = query.filter(CoverOffer.created>get_one_week_ago())
    return [item.__json__() for item in query.all()]

def get_your_promote_offers(request):
    """Get your promotion offers for the current #hashtag."""
    
    query = Session.query(PromoteOffer)
    query = query.filter(PromoteOffer.user==request.user)
    query = query.filter(Assignment.hashtag==request.hashtag)
    query = query.filter(PromoteOffer.created>get_one_week_ago())
    return [item.__json__() for item in query.all()]

def get_own_tweets(request):
    """Get your tweets for the current #hashtag."""
    
    query = Session.query(Tweet)
    query = query.filter(Tweet.user_twitter_id==request.user.twitter_account.twitter_id)
    query = query.filter(Tweet.hashtags.contains(request.hashtag))
    query = query.filter(Tweet.created>get_one_week_ago())
    query = query.filter(Tweet.coverage_records==None)
    return [item.__json__() for item in query.all()]

def get_your_assignments(request):
    """Get a list of your assignments in dict form, sorted by most recent."""
    
    query = Assignment.query.filter_by(author=request.user)
    query = query.filter(Assignment.created>get_one_week_ago())
    query = query.filter(Assignment.hashtag==request.hashtag)
    query = query.order_by(Assignment.created).limit(25)
    return [item.__json__() for item in query.all()]

def get_popular_assignments(request):
    """Get assignments sorted by rating."""
    
    # Cache in redis for five minutes
    KEY = 'beliveat:popular_assignments:{0}'.format(request.hashtag.value)
    results_str = request.redis.get(KEY)
    if results_str:
        results = json.loads(results_str)
    else: # Get the latest 2500 assignments and rank them.  Note that we strip out
        # the assignments from the current user client side, so this function can
        # be cached, seeing how it's so ridiculously expensive.
        compare_function = operator.attrgetter('rank')
        query = Assignment.query.order_by(Assignment.created)
        query = query.filter(Assignment.hashtag==request.hashtag)
        query = query.filter(Assignment.created>get_one_week_ago())
        latest_assignments = query.limit(2500).all()
        latest_assignments.sort(key=compare_function, reverse=True)
        # Return the 25 most popular.
        results = [item.__json__() for item in latest_assignments[:25]]
        results_str = json.dumps(results)
        request.redis.setex(KEY, 300, results_str)
    # Return the list of results.
    return results


@view_config(route_name='dashboard', renderer='beliveat:templates/dashboard.mako')
def dashboard_view(request):
    
    your_assignments = get_your_assignments(request)
    popular_assignments = get_popular_assignments(request)
    cover_offers = get_your_cover_offers(request)
    promote_offers = get_your_promote_offers(request)
    own_tweets = get_own_tweets(request)
    
    # Flag all the assignments that you've offered to cover.
    covering_ids = [item['assignment'] for item in cover_offers]
    for item in your_assignments + popular_assignments:
        item['covering'] = item['id'] in covering_ids
    
    # Flag all the assignments that you've offered to promote.
    promoting_ids = [item['assignment'] for item in promote_offers]
    for item in your_assignments + popular_assignments:
        item['promoting'] = item['id'] in promoting_ids
    
    # Strip out all the closed offers.
    cover_offers = [item for item in cover_offers if not item['closed']]
    promote_offers = [item for item in promote_offers if not item['closed']]
    
    # Return as json strings to write into the template.
    return {
        'your_assignments': json.dumps(your_assignments),
        'popular_assignments': json.dumps(popular_assignments),
        'cover_offers': json.dumps(cover_offers),
        'promote_offers': json.dumps(promote_offers),
        'own_tweets': json.dumps(own_tweets)
    }


"""
@view_config(route_name='assignments', name="your", request_method='GET',
        xhr=True, renderer='json')
def your_assignments_view(request):
    return get_your_assignments(request)

@view_config(route_name='assignments', name="popular", request_method='GET',
        xhr=True, renderer='json', http_cache=timedelta(minutes=5))
def popular_assignments_view(request):
    return get_popular_assignments(request)

@view_config(route_name='dashboard', renderer='json', xhr=True)
def dashboard_ajax_view(request):
    data = dashboard_view(request)
    return {} # data.__json__()

"""



