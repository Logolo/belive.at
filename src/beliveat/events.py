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
    

