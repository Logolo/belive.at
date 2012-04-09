# -*- coding: utf-8 -*-

"""Query the db."""

from pyramid_basemodel import Session
from pyramid_twitterauth.model import TwitterAccount

from .model import Hashtag

def get_all_twitter_ids(session_cls=None):
    """Get all the twitter ids in the db."""
    
    # Test jig.
    if session_cls is None:
        session_cls = Session
    
    query = session_cls.query(TwitterAccount.twitter_id)
    return [item[0] for item in query.all()]


def get_all_hashtags(session_cls=None):
    """Get all the hashtags in the db."""
    
    # Test jig.
    if session_cls is None:
        session_cls = Session
    
    query = session_cls.query(Hashtag.value)
    return [u'#{0}'.format(item[0]) for item in query.all()]

