# -*- coding: utf-8 -*-

"""``Story``, ``Assignment`` and ``Offer`` views."""

import logging
logger = logging.getLogger(__name__)

import json
import operator

from datetime import timedelta

from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound, HTTPForbidden
from pyramid.view import view_config

from pyramid_basemodel import Session, save as save_to_db
from pyramid_simpleform import Form
from pyramid_simpleform.renderers import FormRenderer

from ..interfaces import IOffer, IOfferRoot, IOfferRecord
from ..model import AssignmentRoot
from ..model import Hashtag, Story, Assignment, CoverOffer, PromoteOffer
from ..model import Tweet, CoverageRecord, PromotionRecord
from ..model import get_one_week_ago
from ..schema import CreateAssignment, CreateOffer, LinkOffer

def get_offers(offer_cls, story, user, since=None, assignment_cls=None):
    """Get offers of type ``offer_cls`` that the ``user`` has made for the target
      ``story`` ``since`` the cutoff date.
    """
    
    if since is None:
        since = get_one_week_ago()
    if assignment_cls is None:
        assignment_cls = Assignment
    
    query = offer_cls.query.filter_by(user=user)
    query = query.filter(offer_cls.created>since)
    query = query.filter(assignment_cls.story==story)
    return [item.__json__() for item in query.all()]

def get_tweets(story, user_twitter_id, since=None, tweet_cls=None):
    """Get tweets that the ``user`` has made ``since`` the cutoff date that
      match the target ``story`` and haven't been either linked or hidden.
    """
    
    if since is None:
        since = get_one_week_ago()
    if tweet_cls is None:
        tweet_cls = Tweet
    
    query = tweet_cls.query.filter_by(user_twitter_id=user_twitter_id)
    query = query.filter_by(hidden=False)
    query = query.filter(tweet_cls.hashtags.contains(story.hashtag))
    query = query.filter(tweet_cls.created>since)
    return [item.__json__() for item in query.all()]

def get_assignments(story, user, since=None, assignment_cls=None):
    """Get a list of your assignments in dict form, sorted by most recent."""
    
    if since is None:
        since = get_one_week_ago()
    if assignment_cls is None:
        assignment_cls = Assignment
    
    query = assignment_cls.query.filter_by(author=user, story=story)
    query = query.filter(assignment_cls.created>since)
    query = query.order_by(assignment_cls.created).limit(25)
    return [item.__json__() for item in query.all()]

def get_popular_assignments(story, redis_client, since=None, assignment_cls=None):
    """Get assignments sorted by rating."""
    
    if since is None:
        since = get_one_week_ago()
    if assignment_cls is None:
        assignment_cls = Assignment
    
    # Cache in redis for five minutes
    KEY = 'beliveat:popular_assignments:{0}'.format(story.hashtag.value)
    results_str = redis_client.get(KEY)
    if results_str:
        results = json.loads(results_str)
    else: # Get the latest 2500 assignments and rank them.  Note that we strip out
        # the assignments from the current user client side, so this function can
        # be cached, seeing how it's so ridiculously expensive.
        compare_function = operator.attrgetter('rank')
        query = assignment_cls.query.filter_by(story=story)
        query = query.filter(assignment_cls.created>since)
        query = query.order_by(assignment_cls.created)
        latest_assignments = query.limit(2500).all()
        latest_assignments.sort(key=compare_function, reverse=True)
        # Return the 25 most popular.
        results = [item.__json__() for item in latest_assignments[:25]]
        results_str = json.dumps(results)
        redis_client.setex(KEY, 300, results_str)
    # Return the list of results.
    return results


@view_config(context=Story, renderer='beliveat:templates/story.mako')
def story_view(request):
    """Render a story dashboard page."""
    
    # Unpack the request.
    redis = request.redis
    story = request.context
    user = request.user
    
    # Get a datetime for one week ago.
    since = get_one_week_ago()
    
    # XXX Query the db.
    your_assignments = get_assignments(story, user, since=since)
    popular_assignments = get_popular_assignments(story, redis, since=since)
    cover_offers = get_offers(CoverOffer, story, user, since=since)
    promote_offers = get_offers(PromoteOffer, story, user, since=since)
    own_tweets = get_tweets(story, user.twitter_account.twitter_id, since=since)
    
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


@view_config(context=AssignmentRoot, name='create', request_method='POST',
        xhr=True, renderer='json')
def create_assignment_view(request, form_cls=Form):
    """Create an assignment."""
    
    form = form_cls(request, schema=CreateAssignment)
    if form.validate():
        d = form.data
        assignment = Assignment(title=d['title'], description=d['description'])
        assignment.story = request.context.story
        assignment.author = request.user
        save_to_db(assignment)
        # XXX create promote offer (n.b.: remember if statement so don't show
        # content to it's originator to RT and auth increment the count if
        # it's your own content)
        return assignment.__json__()
    request.response.status_int = 400
    return form.errors


@view_config(context=IOfferRoot, name='create', request_method='POST',
        xhr=True, renderer='json')
def create_offer_view(request, form_cls=Form):
    """Create a cover or a promote offer."""
    
    # Unpack the request / context.
    user = request.user
    offer_cls = request.context.model_cls
    assignment = request.context.assignment
    
    form = form_cls(request, schema=CreateOffer)
    if form.validate():
        # Don't let a user create two offers for the same thing.
        if offer_cls.query.filter_by(assignment=assignment, user=user).first():
            return HTTPBadRequest()
        # Create and save the offer.
        offer = form.bind(offer_cls(assignment=assignment, user=user))
        save_to_db(offer)
        return offer.__json__()
    request.response.status_int = 400
    return form.errors


@view_config(context=IOffer, name='close', request_method='POST', xhr=True,
        renderer='json', permission='edit') 
def close_offer_view(request):
    """Close an offer."""
    
    request.context.closed = True
    save_to_db(request.context)
    return {'status': 'OK'}


@view_config(context=CoverOffer, name='link', request_method='POST', xhr=True,
        renderer='json', permission='edit') 
def close_offer_view(request, form_cls=None, tweet_cls=None, record_cls=None,
        save=None):
    """Link an offer to a Tweet."""
    
    # Test jig.
    if form_cls is None:
        form_cls = Form
    if tweet_cls is None:
        tweet_cls = Tweet
    if record_cls is None:
        record_cls = CoverageRecord
    if save is None:
        save = save_to_db
    
    # Validate the user input.
    form = form_cls(request, schema=LinkOffer)
    if form.validate():
        # - make sure the tweet exists
        tweet = tweet_cls.query.get(form.data['id'])
        if not tweet:
            return HTTPNotFound()
        # - make sure the tweet was posted by the authenticated user
        if not request.user.twitter_account.twitter_id == tweet.user_twitter_id:
            return HTTPForbidden()
        # - make sure the tweet hasn't already been linked to this offer
        query = record_cls.query.filter_by(offer=request.context, tweet=tweet)
        existing = query.first()
        if existing:
            return HTTPBadRequest()
        # Create and save the coverage record.
        record = CoverageRecord(offer=request.context, tweet=tweet)
        save(record)
        return record.__json__()
    request.response.status_int = 400
    return form.errors

