# -*- coding: utf-8 -*-

"""Notify in response to ORM events."""

import logging
logger = logging.getLogger(__name__)

import json

from pyramid.events import subscriber
from pyramid_twitterauth import model as twitterauth_model

from .events import StoryAdded, StoryEdited, StoryDeleted
from .events import TweetAdded, CoverageRecordAdded, PromotionRecordAdded
from .hooks import get_redis_client
from .model import Hashtag, Story, CoverOffer, PromoteOffer
from .tx import join_to_transaction

STREAM_MANAGER_NOTIFICATION_CHANNEL = 'beliveat.stream:instructions'

def trigger_reconnect(redis_client, key=None, join=None):
    """Tell the Twitter streaming API consumer manager that it needs to reconnect."""
    
    if key is None:
        key = STREAM_MANAGER_NOTIFICATION_CHANNEL
    if join is None:
        join = join_to_transaction
    
    # Add an after commit hook to push the notification to the redis channel.
    join(redis_client.rpush, key, 'consumer:reload')


@subscriber(StoryAdded)
def handle_story_added(event):
    trigger_reconnect(event.request.redis)


@subscriber(StoryEdited)
def handle_story_edited(event):
    trigger_reconnect(event.request.redis)


@subscriber(StoryDeleted)
def handle_story_deleted(event):
    trigger_reconnect(event.request.redis)


@subscriber(TweetAdded)
def handle_tweet_added(event, join=None, get_redis=None, offer_cls=None,
        hashtag_cls=None, account_cls=None):
    """Notify all the users who might want to use this Tweet to cover
      an assignment.
    """
    
    logger.warn('handle_tweet_added')
    
    # Test jig.
    if join is None:
        join = join_to_transaction
    if get_redis is None:
        get_redis = get_redis_client
    if offer_cls is None:
        offer_cls = CoverOffer
    if hashtag_cls is None:
        hashtag_cls = Hashtag
    if account_cls is None:
        account_cls = twitterauth_model.TwitterAccount
    
    # Unpack the event.
    tweet = event.tweet
    message = tweet.body.encode('utf-8')
    twitter_id = tweet.user_twitter_id
    
    # Get all the potentially relevant cover offers.
    hashtag_values = [item.value for item in tweet.hashtags]
    query = offer_cls.query.filter(hashtag_cls.value.in_(hashtag_values))
    query = query.filter(account_cls.twitter_id==twitter_id)
    query = query.filter_by(closed=False)
    
    # Use it to build a list of channels.
    channels = []
    for offer in query.all():
        hashtag = offer.assignment.story.hashtag.value
        canonical_id = offer.user.canonical_id
        channel = 'own_tweet:{0}:{1}'.format(hashtag, canonical_id)
        channels.append(channel)
    
    # Add an after commit hook to publish to each of the channels.
    redis_client = get_redis()
    for channel in channels:
        join(redis_client.publish, channel, message)
    


@subscriber(CoverageRecordAdded)
def handle_coverage_record_added(event, join=None, get_redis=None, offer_cls=None):
    """Notify all the users who've offered to promote the relevant assignment."""
    
    logger.warn('handle_coverage_record_added')
    
    # Test jig.
    if join is None:
        join = join_to_transaction
    if get_redis is None:
        get_redis = get_redis_client
    if offer_cls is None:
        offer_cls = PromoteOffer
    
    # Unpack the event.
    assignment = event.record.offer.assignment
    tweet = event.record.tweet
    tweet_data = json.loads(tweet.body)
    
    # Get all the potentially relevant promote offers.
    query = offer_cls.query.filter_by(assignment=assignment, closed=False)
    
    # Add an after commit hook to publish to each of them.
    redis_client = get_redis()
    for offer in query.all():
        # Build the message
        # Build the channel.
        hashtag = offer.assignment.story.hashtag.value
        canonical_id = offer.user.canonical_id
        channel = 'tweet_to_promote:{0}:{1}'.format(hashtag, canonical_id)
        # Publish the message to the channel, sending through the target promote
        # offer's id as well as the tweet data.
        message_data = {
            'tweet': tweet_data,
            'offer': offer.public_id
        }
        join(redis_client.publish, channel, json.dumps(message_data))


@subscriber(PromotionRecordAdded)
def post_retweet(event, join=None):
    """If the promotion record's action_code matches, then post the RT."""
    
    logger.warn('Posting RT...')
    
    # Test jig.
    if join is None:
        join = join_to_transaction
    
    # Unpack the event.
    request = event.request
    record = event.record
    
    # Ignore any records that weren't to amplify.
    if record.action_code != request.action_codes['amplify']:
        return
    
    # Add an after commit hook to post the RT.
    join(request.twitter.client.retweet, record.tweet.id)
    


@subscriber(PromotionRecordAdded)
def handle_promotion_record_added(event, join=None, get_redis=None, offer_cls=None):
    """"""
    
    logger.warn('XXX notify users when a promotion record happens')

