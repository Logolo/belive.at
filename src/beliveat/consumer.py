#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Consumes tweets from the Twitter Streaming API and puts them on a 
  `Beanstalkd` queue.  In addition, it listens to the ``belive.tweets``
  Beanstalkd queue, for:
  
  * new hashtags to add to the follow predicates
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

import ConfigParser
import json
import logging
import sys
import transaction
import threading
import time

import argparse
import beanstalkc
import tweepy
import ttp

from sqlalchemy import create_engine
from pyramid_basemodel import Session, bind_engine, save as save_to_db

from .model import Hashtag, Tweet, TweetRecord
from .query import get_all_hashtags, get_all_twitter_ids

def beanstalk_factory(input_queue, output_queue, cls=beanstalkc.Connection):
    """Return a configured beanstalkd client."""
    
    client = cls(host='localhost', port=11300)
    client.use(output_queue)
    client.watch(input_queue)
    for item in client.tubes()[:-1]:
        client.ignore(item)
    return client

def oauth_handler_factory(config, section_key='app:beliveat', cls=tweepy.OAuthHandler):
    """Return an authenticated Twitter Streaming API consumer.
      
          >>> raise NotImplementedError
      
    """
    
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


class StreamListener(tweepy.StreamListener):
    """Handle data from the Streaming API client."""
    
    def on_data(self, raw_data):
        """Called when raw data is received from connection."""
        
        # Decode into a unicode string.
        text = unicode(raw_data, 'utf-8')
        # Call the handle_function
        self.handle_function(text)
    
    def on_error(self, status_code):
        logging.warn('Error: status code %s' % status_code)
        return True # keep stream alive
    
    def on_timeout(self):
        logging.info('timeout')
    
    def __init__(self, handle_function, api=None):
        
        logging.info('StreamListener()')
        
        super(StreamListener, self).__init__(api=api)
        self.handle_function = handle_function
    

class QueueProcessor(object):
    """Listen for new follow ids from the beanstalk queue.  When one arrives, 
      pass it to the ``handler_function``.
    """
    
    running = False
    
    def stop(self):
        """Call ``stop()`` to stop processing the queue the next time a job is
          processed or the input queue timeout is reached.
        """
        
        logging.info('QueueProcessor.stop()')
        
        self.running = False
    
    def _start(self, timeout=5):
        """Call ``start()`` to start processing the input queue(s)."""
        
        logging.info('QueueProcessor.start(timeout=%d)' % timeout)
        
        self.running = True
        while self.running:
            try:
                job = self.beanstalk.reserve(timeout=timeout)
            except Exception as err:
                logging.warn(err)
                time.sleep(10)
            else:
                if job:
                    try:
                        self.handle_function(job.body)
                    except Exception as err:
                        logging.warning(err)
                        logging.warning(job.body)
                    finally:
                        job.delete()
    
    def start(self, async=False):
        """Either start running or start running in a thread."""
        
        if self.running:
            return
        
        if async:
            threading.Thread(target=self._start).start()
        else:
            self._start()
    
    def __init__(self, beanstalk, handle_function):
        
        self.beanstalk = beanstalk
        self.handle_function = handle_function
    

class Manager(object):
    """Load the follow ids from the database and start a streaming api client
      and a beanstalk queue procesor.  When a new follow id comes form beanstalk,
      add it to the follow ids and restart the client.
    """
    
    clients = []
    
    follow_ids = []
    track_keywords = []
    
    def handle_twitter_data(self, text):
        """"""
        
        # If the text doesn't looks valid, ignore it.
        is_status = 'in_reply_to_status_id' in text
        is_deletion = 'delete' in text
        if not bool(is_status or is_deletion):
            return
        # Try to parse the JSON text into a data dict.
        try:
            data = json.loads(text)
        except Exception as err:
            logging.warn(err)
            return
        # Inside a transaction.
        with transaction.manager:
            # If we're dealing with a status.
            if data.has_key('in_reply_to_status_id'):
                # If it's a RT...
                if data.has_key('retweeted_status'):
                    record = TweetRecord(is_retweet=True, is_reply=False)
                    record.tweet_id = data['retweeted_status']['id']
                    record.by_user_twitter_id = data['user']['id']
                    save_to_db(record)
                    of = data['retweeted_status']['user']['screen_name']
                    by = data['user']['screen_name']
                    logging.info('RT of @{0} by @{1}.'.format(of, by))
                # If it's a reply...
                elif data.get('in_reply_to_user_id'):
                    record = TweetRecord(is_retweet=False, is_reply=True)
                    record.tweet_id = data['in_reply_to_status_id']
                    record.by_user_twitter_id = data['user']['id']
                    save_to_db(record)
                    to = data['in_reply_to_screen_name']
                    by = data['user']['screen_name']
                    logging.info('@reply to @{0} by @{1}.'.format(to, by))
                # If it's a normal tweet that we haven't seen already...
                elif not Tweet.query.get(data['id']):
                    tweet = Tweet(id=data['id'])
                    tweet.body = text
                    tweet.user_twitter_id = data['user']['id']
                    for item in ttp.Parser().parse(data['text']).tags:
                        item = item.lower()
                        query = Hashtag.query
                        hashtag = query.filter_by(value=item).first()
                        if not hashtag:
                            hashtag = Hashtag(value=item)
                        tweet.hashtags.append(hashtag)
                    save_to_db(tweet)
                    from_ = data['user']['screen_name']
                    text = data['text']
                    logging.info(u'@{0}: {1}'.format(from_, text))
            # Else if it's a deletion record, delete the corresponding tweet.
            elif data.has_key('delete'):
                id_ = data['delete']['status']['id']
                tweet = Tweet.query.get(id_)
                if tweet:
                    Session.delete(tweet)
                logging.info('Deleted %d' % id_)
    
    def handle_queue_data(self, text):
        """We accept two different instructions from the beanstalk queue:
          
          1. if passed a string in the form ``follow:int_follow_id`` add
             ``int_follow_id`` to the follow ids and reconnect
          2. if passed a string in the form ``track:keyword`` add ``keyword``
             to the track predicates and reconnect
          3. if passed "consumer:reload", reconnect
          
        """
        
        logging.info('Manager.handle_queue_data()')
        logging.info(text)
        
        # We don't want to fire up a new client if we're already closing.
        if not self.running:
            return
        
        # If explicitly told to, reload the follower ids and reconnect.
        if text == 'consumer:reload':
            self.reload_predicates()
            return self.reconnect()
        
        # Otherwise, if it's a follower id.
        if text.startswith('follow:'):
            try: # Parse the text into an int follower id.
                follower_id = int(text[7:])
            except ValueError as err:
                logging.warn(err)
            else: # Follow the new user and reload.
                if not bool(follower_id in self.follower_ids):
                    self.follower_ids.append(follower_id)
                    return self.reconnect()
        
        # Otherwise, if it's a track predicate.
        if text.startswith('track:'):
            try: # Parse the text into a keyword.
                keyword = text[6:].strip()
            except ValueError as err:
                logging.warn(err)
            else: # Follow the new user and reload.
                if not bool(keyword in self.track_keywords):
                    self.track_keywords.append(keyword)
                    return self.reconnect()
    
    def reload_predicates(self):
        """Load the filter predicates.  XXX for now, we follow all Twitter users
          and all Hashtags.  In time, we'll need to put a cap on this.
        """
        
        logging.warn('XXX Need to actually use the appropriate predicates.')
        
        #self.follow_ids = get_all_twitter_ids()
        #self.track_keywords = get_all_hashtags()
        
        self.track_keywords = ['#syria']
    
    def reconnect(self):
        """Disconnect existing clients and fire up a new one."""
        
        self.disconnect_existing_clients()
        self.fire_up_new_client()
    
    def disconnect_existing_clients(self):
        """Tell all the existing clients to disconnect."""
        
        logging.info('Manager.disconnect_existing_clients()')
        
        for client in self.clients:
            client.disconnect()
            self.clients.remove(client)
    
    def fire_up_new_client(self, cls=tweepy.streaming.Stream):
        """Create a new streaming client and start it going."""
        
        logging.info('Manager.fire_up_new_client()')
        
        client = cls(self.oauth_handler, self.stream_listener, timeout=55)
        client.filter(follow=self.follow_ids, track=self.track_keywords, async=True)
        self.clients.append(client)
    
    def stop(self):
        """Stop the processor and disconnect the clients."""
        
        logging.info('Manager.stop()')
        
        self.running = False
        self.processor.stop()
        self.disconnect_existing_clients()
    
    def start(self):
        """Loop forever.  If there isn't an active client, fire one up.  If the
          queue processor isn't running, fire that up.
        """
        
        logging.info('Manager.start()')
        
        self.running = True
        self.processor.start(async=True)
        while self.running:
            if not self.clients or not self.clients[-1].running:
                self.fire_up_new_client()
            time.sleep(1)
    
    def __init__(self, beanstalk_client, oauth_handler):
        """Setup the stream listener ready to handle data, the streaming api
          auth handler and queue processor and load the follow ids.
        """
        
        logging.info('Manager.__init__()')
        
        # Setup the stream listener, telling it to pass data from the streaming
        # api to ``self.handle_twitter_data``.
        self.stream_listener = StreamListener(self.handle_twitter_data)
        # Setup the queue processor, telling it to pass data from the beanstalk
        # client to ``self.handle_queue_data``.
        self.processor = QueueProcessor(beanstalk_client, self.handle_queue_data)
        # Save a handle on the Twitter oauth handler.
        self.oauth_handler = oauth_handler
        # Load the filter predicates.
        self.reload_predicates()
    


def main(args=None):
    """Main entry point (uses the first command line arg as the log level)."""
    
    # Parse the command line unless ``args`` has been passed in.
    parser = argparse.ArgumentParser()
    parser.add_argument('config_file', metavar='CONFIG_FILE', nargs=1,
            help='The .ini file to look for the Twitter config in?')
    parser.add_argument("--input-queue", dest="input_queue", default='beliveat_input',
            help="Name of the beanstalk tube to consume. Defaults to %(default)s.")
    parser.add_argument("--output-queue", dest="output_queue", default='beliveat_output',
            help="Name of the beanstalk tube to output to. Defaults to %(default)s.")
    parser.add_argument("--log-level", dest="log_level", default='INFO',
            help='Logging level. Defaults to %(default)s.')
    if args is None: # pragma
        args = parser.parse_args()
    
    # Setup logging.
    level = getattr(logging, args.log_level)
    logging.basicConfig(level=args.log_level)
    
    # Setup the beanstalk client.
    beanstalk_client = beanstalk_factory(args.input_queue, args.output_queue)
    
    # Setup the oauth handler.
    config = ConfigParser.SafeConfigParser()
    config.read(args.config_file)
    oauth_handler = oauth_handler_factory(config)
    
    # Bind the model classes.
    engine = create_engine(config.get('app:beliveat', 'sqlalchemy.url'))
    bind_engine(engine)
    
    # Instantiate a ``Manager`` and start it running.
    manager = Manager(beanstalk_client, oauth_handler)
    try:
        manager.start()
    except KeyboardInterrupt:
        manager.stop()


if __name__ == '__main__':
    main()

