# -*- coding: utf-8 -*-

"""Events fired in response to user actions."""

import logging
logger = logging.getLogger(__name__)

from zope.interface import implementer, Attribute, Interface

class IStoryAdded(Interface):
    """An event type that is emitted when a story is added."""
    
    request = Attribute('Request object.')
    story = Attribute('Story instance.')

class IStoryEdited(Interface):
    """An event type that is emitted when a story is edited."""
    
    request = Attribute('Request object.')
    story = Attribute('Story instance.')

class IStoryDeleted(Interface):
    """An event type that is emitted when a story is deleted."""
    
    request = Attribute('Request object.')
    story = Attribute('Story instance.')


class ITweetAdded(Interface):
    """An event type that is emitted when a tweet is added."""
    
    request = Attribute('Request object.')
    tweet = Attribute('Tweet instance.')

class ICoverageRecordAdded(Interface):
    """An event type that is emitted when a coverage record is added."""
    
    request = Attribute('Request object.')
    record = Attribute('CoverageRecord instance.')

class IPromotionRecordAdded(Interface):
    """An event type that is emitted when a promotion record is added."""
    
    request = Attribute('Request object.')
    record = Attribute('PromotionRecord instance.')


@implementer(IStoryAdded)
class StoryAdded(object):
    """An instance of this class is emitted whenever a story is added."""
    
    def __init__(self, request, story, data=None):
        self.request = request
        self.story = story
        self.data = data
    

@implementer(IStoryEdited)
class StoryEdited(object):
    """An instance of this class is emitted whenever a story is edited."""
    
    def __init__(self, request, story, data=None):
        self.request = request
        self.story = story
        self.data = data
    

@implementer(IStoryDeleted)
class StoryDeleted(object):
    """An instance of this class is emitted whenever a story is deleted."""
    
    def __init__(self, request, story, data=None):
        self.request = request
        self.story = story
        self.data = data
    


@implementer(ITweetAdded)
class TweetAdded(object):
    """An instance of this class is emitted whenever a tweet is added."""
    
    def __init__(self, request, tweet, data=None):
        self.request = request
        self.tweet = tweet
        self.data = data
    

@implementer(ICoverageRecordAdded)
class CoverageRecordAdded(object):
    """An instance of this class is emitted when a coverage record is added."""
    
    def __init__(self, request, record, data=None):
        self.request = request
        self.record = record
        self.data = data
    

@implementer(IPromotionRecordAdded)
class PromotionRecordAdded(object):
    """An instance of this class is emitted when a promotion record is added."""
    
    def __init__(self, request, record, data=None):
        self.request = request
        self.record = record
        self.data = data
    

