#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Consumes tweets from the Twitter Streaming API and puts them on a 
  redis queue.  In addition, it listens to the redis queue, for:
  
  * new hashtags and follower ids to add to the track predicates
  * a "reload" instruction
  
  XXX implement the ``manager.reload_predicates()`` method to actually follow
  the right users and keywords.  For now, we've hardcoded to just track "#syria".
  
  Under the hood, the queue processor and the streaming consumer are both run
  in their own threads.  The local queue processor is resilient but the Twitter 
  Streaming Api enjoys falling over.  When it does, the active client will set 
  ``self.running`` to ``False``.  In the main control thread, we poll this flag
  every second and fire up a new client whenever it falls over.
  
  We'll miss a tweet every now and then but that's not the end of the world.
"""

import logging
import logging.config
logger = logging.getLogger(__name__)

import argparse
import ConfigParser
import os
import threading
import time
import tweepy

from sqlalchemy import create_engine

from pyramid_basemodel import Session, bind_engine
from pyramid_twitterauth.model import TwitterAccount

from .hooks import get_redis_client
from .model import Hashtag
from .queue import QueueProcessor

INPUT_CHANNEL = 'beliveat.stream:instructions'
OUTPUT_CHANNEL = 'beliveat.queue:input'

def oauth_handler_factory(config, section_key='app:beliveat', cls=tweepy.OAuthHandler):
    """Return an authenticated Twitter Streaming API consumer."""
    
    # Create the handler.
    k = section_key
    consumer_key = config.get(k, 'twitterauth.oauth_consumer_key')
    consumer_secret = config.get(k, 'twitterauth.oauth_consumer_secret')
    handler = cls(consumer_key, consumer_secret, secure=True)
    
    # Set the access token.
    access_token_key = config.get(k, 'twitter_consumer.access_token_key')
    access_token_secret = config.get(k, 'twitter_consumer.access_token_secret')
    handler.set_access_token(access_token_key, access_token_secret)
    
    # Return the authenticated handler.
    return handler


def get_all_twitter_ids(session_cls=None):
    """Get all the twitter ids in the db."""
    
    # Test jig.
    if session_cls is None:
        session_cls = Session
    
    query = session_cls.query(TwitterAccount.twitter_id).limit(5000)
    return [item[0] for item in query.all()]

def get_track_keywords(hashtag_cls=None):
    """Get the hashtag values of all the active stories."""
    
    # Test jig.
    if hashtag_cls is None:
        hashtag_cls = Hashtag
    
    query = hashtag_cls.query.filter(hashtag_cls.story!=None)
    query = query.order_by(hashtag_cls.modified.desc()).limit(400)
    hashtags = query.all()
    return [u'#{0}'.format(item.value) for item in hashtags]


class StreamListener(tweepy.StreamListener):
    """Handle data from the Streaming API client."""
    
    def on_data(self, data_str):
        """Called when raw data is received from connection."""
        
        # Call the handle_function
        self.handle_function(data_str)
    
    def on_error(self, status_code):
        logger.warn('Error: status code %s' % status_code)
        return True # keep stream alive
    
    def on_timeout(self):
        logger.info('timeout')
    
    def __init__(self, handle_function, api=None):
        
        logger.info('StreamListener()')
        
        super(StreamListener, self).__init__(api=api)
        self.handle_function = handle_function
    

class Manager(object):
    """Load the follow ids from the database and start a streaming api client
      and a redis queue procesor.  When a new follow id comes form redis,
      add it to the follow ids and restart the client.
    """
    
    clients = []
    
    follow_ids = []
    track_keywords = []
    
    def handle_twitter_data(self, data_str):
        """Put incoming tweets onto the redis queue."""
        
        # If the text doesn't looks valid, ignore it.
        is_status = 'in_reply_to_status_id' in data_str
        is_deletion = 'delete' in data_str
        if not bool(is_status or is_deletion):
            return
        
        # Otherwise put it on the output queue.
        self.redis.rpush(self.output_channel, data_str)
    
    def handle_queue_data(self, data_str):
        """We accept two different instructions from the redis queue:
          
          1. if passed a string in the form ``follow:int_follow_id`` add
             ``int_follow_id`` to the follow ids and reconnect
          2. if passed a string in the form ``track:keyword`` add ``keyword``
             to the track predicates and reconnect
          3. if passed "consumer:reload", reconnect
          
        """
        
        logger.info('Manager.handle_queue_data()')
        logger.info(data_str)
        
        # We don't want to fire up a new client if we're already closing.
        if not self.running:
            return
        
        # Decode to unicode.
        text = unicode(data_str, 'utf-8')
        
        # If explicitly told to, reload the follower ids and reconnect.
        if text == 'consumer:reload':
            self.reload_predicates()
            return self.reconnect()
        
        # Otherwise, if it's a follower id.
        if text.startswith('follow:'):
            try: # Parse the text into an int follower id.
                follower_id = int(text[7:])
            except ValueError as err:
                logger.warn(err)
            else: # Follow the new user and reload.
                if not bool(follower_id in self.follower_ids):
                    self.follower_ids.append(follower_id)
                    return self.reconnect()
        
        # Otherwise, if it's a track predicate.
        if text.startswith('track:'):
            try: # Parse the text into a keyword.
                keyword = text[6:].strip()
            except ValueError as err:
                logger.warn(err)
            else: # Follow the new user and reload.
                if not bool(keyword in self.track_keywords):
                    self.track_keywords.append(keyword)
                    return self.reconnect()
    
    def reload_predicates(self, get_twitter_ids=None, get_keywords=None):
        """Load the filter predicates."""
        
        logger.warn('Reloading predicates...')
        logger.warn('- current:')
        logger.warn(self.follow_ids)
        logger.warn(self.track_keywords)
        
        if get_twitter_ids is None:
            get_twitter_ids = get_all_twitter_ids
        if get_keywords is None:
            get_keywords = get_track_keywords
        
        self.follow_ids = get_twitter_ids()
        self.track_keywords = get_keywords()
        
        logger.warn('- new:')
        logger.warn(self.follow_ids)
        logger.warn(self.track_keywords)
    
    def reconnect(self):
        """Disconnect existing clients and fire up a new one."""
        
        self.disconnect_existing_clients()
        self.fire_up_new_client()
    
    def disconnect_existing_clients(self):
        """Tell all the existing clients to disconnect."""
        
        logger.info('Manager.disconnect_existing_clients()')
        
        for client in self.clients:
            client.disconnect()
            self.clients.remove(client)
    
    def fire_up_new_client(self, cls=tweepy.streaming.Stream):
        """Create a new streaming client and start it going."""
        
        logger.info('Manager.fire_up_new_client()')
        
        client = cls(self.oauth_handler, self.stream_listener, timeout=35)
        client.filter(follow=self.follow_ids, track=self.track_keywords, async=True)
        self.clients.append(client)
    
    def stop(self):
        """Stop the processor and disconnect the clients."""
        
        logger.info('Manager.stop()')
        
        self.running = False
        self.processor.stop()
        self.disconnect_existing_clients()
    
    def start(self):
        """Loop forever.  If there isn't an active client, fire one up.  If the
          queue processor isn't running, fire that up.
        """
        
        logger.info('Manager.start()')
        
        self.running = True
        self.processor.start(async=True)
        while self.running:
            if not self.clients or not self.clients[-1].running:
                self.fire_up_new_client()
            time.sleep(1)
    
    def __init__(self, redis_client, oauth_handler, input_channel, output_channel):
        """Setup the stream listener ready to handle data, the streaming api
          auth handler and queue processor and load the follow ids.
        """
        
        logger.info('Manager.__init__()')
        
        # Setup the stream listener, telling it to pass data from the streaming
        # api to ``self.handle_twitter_data``.
        self.stream_listener = StreamListener(self.handle_twitter_data)
        # Setup the queue processor, telling it to pass data from the redis
        # client to ``self.handle_queue_data``.
        self.redis = redis_client
        self.output_channel = output_channel
        self.processor = QueueProcessor(redis_client, [input_channel],
                self.handle_queue_data)
        # Save a handle on the Twitter oauth handler.
        self.oauth_handler = oauth_handler
        # Load the filter predicates.
        self.reload_predicates()
    


def parse_args(parser_cls=argparse.ArgumentParser):
    """Parse the command line arguments."""
    
    parser = parser_cls()
    parser.add_argument('config_file', metavar='CONFIG_FILE', nargs=1)
    parser.add_argument("--input", dest="input_channel", default=INPUT_CHANNEL)
    parser.add_argument("--output", dest="output_channel", default=OUTPUT_CHANNEL)
    return parser.parse_args()

def main(args=None):
    """Consume the Twitter Streaming API."""
    
    # Write a pid file.
    f = open('stream.pid', 'w')
    f.write(str(os.getpid()))
    f.close()
    
    # Parse the command line args.
    if args is None:
        args = parse_args()
    
    # Read the config file.
    config = ConfigParser.SafeConfigParser()
    config.read(args.config_file)
    
    # Setup logging.
    logging.config.fileConfig(args.config_file)
    
    # Patch sockets and threading.
    from gevent import monkey
    monkey.patch_all()
    
    # Bind the model classes.
    engine = create_engine(config.get('app:beliveat', 'sqlalchemy.url'))
    bind_engine(engine)
    
    # Instantiate a ``Manager`` with a redis client and oauth handler and
    # start the manager running.
    client = get_redis_client()
    handler = oauth_handler_factory(config)
    manager = Manager(client, handler, args.input_channel, args.output_channel)
    try:
        manager.start()
    except KeyboardInterrupt:
        manager.stop()


if __name__ == '__main__':
    main()

