# -*- coding: utf-8 -*-

"""Handle tweet data."""

import logging
logger = logging.getLogger(__name__)

import json

from pyramid.threadlocal import get_current_registry

from pyramid_basemodel import Session, save as save_to_db
from pyramid_twitterauth.model import TwitterAccount

from .events import TweetAdded
from .model import Hashtag, Tweet, TweetRecord
from .notify import handle_tweet_added
from .schema import Hashtag as ValidHashtag

def handle_retweet(data, model_cls=TweetRecord, save=save_to_db):
    """Record a retweet from the Twitter API."""
    
    record = model_cls(is_retweet=True, is_reply=False)
    record.tweet_id = data['retweeted_status']['id']
    record.by_user_twitter_id = data['user']['id']
    save(record)
    
    # XXX debug.
    of = data['retweeted_status']['user']['screen_name']
    by = data['user']['screen_name']
    logger.info('RT of @{0} by @{1}.'.format(of, by))

def handle_reply(data, model_cls=TweetRecord, save=save_to_db):
    """Record an ``@reply``."""
    
    record = model_cls(is_retweet=False, is_reply=True)
    record.tweet_id = data['in_reply_to_status_id']
    record.by_user_twitter_id = data['user']['id']
    save(record)
    
    # XXX debug.
    to = data['in_reply_to_screen_name']
    by = data['user']['screen_name']
    logger.info('@reply to @{0} by @{1}.'.format(to, by))

def handle_tweet(data, text, tweet_cls=Tweet, hashtag_cls=Hashtag, save=save_to_db):
    """Store the Tweet."""
    
    # XXX this is all *incredibly* inefficient...
    
    # If we already have the Tweet, then ignore this duplicate.
    existing = tweet_cls.query.get(data['id'])
    if existing:
        return
    
    # If the tweet isn't from one of our users, then ignore it.
    twitter_id = data['user']['id']
    query = TwitterAccount.query.filter_by(twitter_id=twitter_id)
    twitter_account = query.first()
    if not twitter_account:
        return
    
    # Store it in the db.
    tweet = tweet_cls(id=data['id'])
    tweet.body = json.dumps(data)
    tweet.user_twitter_id = data['user']['id']
    tag_entities = data.get('entities', {}).get('hashtags', [])
    for item in tag_entities:
        value = ValidHashtag.to_python(item['text'])
        tweet.hashtags.append(hashtag_cls.get_or_create(value))
    save(tweet)
    
    # Notify.
    handle_tweet_added(TweetAdded(None, tweet))
    
    from_ = data['user']['screen_name']
    text = data['text']
    logger.warn(u'@{0}: {1}'.format(from_, text))

def handle_status(data, text):
    """Handle a Twitter status."""
    
    # If it's a RT...
    if data.has_key('retweeted_status'):
        return None # handle_retweet(data)
    # If it's a reply...
    if data.get('in_reply_to_user_id'):
        return None # handle_reply(data)
    # It's a normal tweet.
    return handle_tweet(data, text)

def handle_deletion(data):
    """Handle a Twitter status."""
    
    id_ = data['delete']['status']['id']
    tweet = Tweet.query.get(id_)
    if tweet:
        Session.delete(tweet)
    
    # XXX debug.
    logger.info('Deleted %d' % id_)

