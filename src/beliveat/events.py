# -*- coding: utf-8 -*-

"""Event handlers."""

import logging
import ttp

from pyramid_basemodel import Session, save as save_to_db
from pyramid_simpleauth.model import User
from pyramid_twitterauth.model import TwitterAccount

from .hooks import get_redis_client
from .model import CoverOffer, Hashtag, Tweet, TweetRecord

def handle_retweet(data, model_cls=TweetRecord, save=save_to_db):
    """Record a retweet from the Twitter API."""
    
    record = model_cls(is_retweet=True, is_reply=False)
    record.tweet_id = data['retweeted_status']['id']
    record.by_user_twitter_id = data['user']['id']
    save(record)
    
    # XXX debug.
    of = data['retweeted_status']['user']['screen_name']
    by = data['user']['screen_name']
    logging.info('RT of @{0} by @{1}.'.format(of, by))

def handle_reply(data, model_cls=TweetRecord, save=save_to_db):
    """Record an ``@reply``."""
    
    record = model_cls(is_retweet=False, is_reply=True)
    record.tweet_id = data['in_reply_to_status_id']
    record.by_user_twitter_id = data['user']['id']
    save(record)
    
    # XXX debug.
    to = data['in_reply_to_screen_name']
    by = data['user']['screen_name']
    logging.info('@reply to @{0} by @{1}.'.format(to, by))

def handle_tweet(data, text, tweet_cls=Tweet, hashtag_cls=Hashtag, save=save_to_db):
    """Store the Tweet."""
    
    # If we already have the Tweet, then ignore this duplicate.
    existing = tweet_cls.query.get(data['id'])
    if existing:
        return
    
    # Store it in the db.
    tweet = tweet_cls(id=data['id'])
    tweet.body = text
    tweet.user_twitter_id = data['user']['id']
    for item in ttp.Parser().parse(data['text']).tags:
        item = item.lower()
        query = hashtag_cls.query
        hashtag = query.filter_by(value=item).first()
        if not hashtag:
            hashtag = hashtag_cls(value=item)
        tweet.hashtags.append(hashtag)
        save(tweet)
    
    # Notify all the users who might want to use this Tweet to cover an assignment.
    hashtag_values = [item.value for item in tweet.hashtags]
    query = CoverOffer.query.filter(Hashtag.value.in_(hashtag_values))
    query = query.filter(TwitterAccount.twitter_id==tweet.user_twitter_id)
    
    logging.warn('XXX will we delete ``CoverOffer``s or retire them?')
    
    redis_client = get_redis_client()
    for offer in query.all():
        canonical_id = offer.user.canonical_id
        channel = 'tweet.{0}'.format(canonical_id)
        redis_client.publish(channel, tweet.__json__())
        logging.info(u'Notifying {0} of new tweet'.format(offer.user.username))
    
    # XXX debug.
    from_ = data['user']['screen_name']
    text = data['text']
    logging.info(u'@{0}: {1}'.format(from_, text))

def handle_status(data, text):
    """Handle a Twitter status."""
    
    # If it's a RT...
    if data.has_key('retweeted_status'):
        return handle_retweet(data)
    # If it's a reply...
    if data.get('in_reply_to_user_id'):
        return handle_reply(data)
    # It's a normal tweet.
    return handle_tweet(data, text)

def handle_deletion(data):
    """Handle a Twitter status."""
    
    id_ = data['delete']['status']['id']
    tweet = Tweet.query.get(id_)
    if tweet:
        Session.delete(tweet)
    
    # XXX debug.
    logging.info('Deleted %d' % id_)

