# -*- coding: utf-8 -*-

"""Notify in response to ORM events."""

import logging
logger = logging.getLogger(__name__)

from pyramid.events import subscriber

from .events import StoryAdded, StoryEdited, StoryDeleted
from .stream import INPUT_CHANNEL as STREAM_MANAGER_NOTIFICATION_CHANNEL
from .tx import join_to_transaction

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

