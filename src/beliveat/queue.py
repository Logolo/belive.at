#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Processes data put on a redis queue."""

import logging
import logging.config
logger = logging.getLogger(__name__)

import argparse
import ConfigParser
import json
import sys
import threading
import time
import transaction

from sqlalchemy import create_engine
from pyramid_basemodel import bind_engine

from .events import handle_deletion, handle_status
from .hooks import get_redis_client

INPUT_CHANNEL = 'beliveat.queue:input'

class QueueProcessor(object):
    """Listen for new follow ids from the beanstalk queue.  When one arrives, 
      pass it to the ``handler_function``.
    """
    
    running = False
    
    def stop(self):
        """Call ``stop()`` to stop processing the queue the next time a job is
          processed or the input queue timeout is reached.
        """
        
        logger.info('QueueProcessor.stop()')
        
        self.running = False
    
    def _start(self, timeout=5):
        """Call ``start()`` to start processing the input queue(s)."""
        
        logger.info('QueueProcessor.start(timeout=%d)' % timeout)
        
        self.running = True
        while self.running:
            try:
                return_value = self.redis.blpop(self.channels, timeout=timeout)
            except Exception as err:
                logger.warn(err)
                time.sleep(10)
            else:
                if return_value is not None:
                    body = return_value[1]
                    try:
                        self.handle_function(body)
                    except Exception as err:
                        logger.warning(err, exc_info=True)
                        logger.warning(body)
    
    def start(self, async=False):
        """Either start running or start running in a thread."""
        
        if self.running:
            return
        
        if async:
            threading.Thread(target=self._start).start()
        else:
            self._start()
    
    def __init__(self, redis_client, channels, handle_function):
        
        self.redis = redis_client
        self.channels = channels
        self.handle_function = handle_function
    


def handle_data(data_str):
    """Handle data from the Twitter Streaming API, via the redis queue."""
    
    # Decode into a unicode string.
    text = unicode(data_str, 'utf-8')
    
    # Try to parse the JSON text into a data dict.
    try:
        data = json.loads(text)
    except Exception as err:
        return logger.warn(err)
    
    # In a transaction.
    with transaction.manager:
        # If we're dealing with a status.
        if data.has_key('in_reply_to_status_id'):
            return handle_status(data, text)
        # If we're dealing with a deletion record.
        if data.has_key('delete'):
            return handle_deletion(data)
        # XXX more events, e.g.: handle verification.


def parse_args(parser_cls=argparse.ArgumentParser):
    """Parse the command line arguments."""
    
    parser = parser_cls()
    parser.add_argument('config_file', metavar='CONFIG_FILE', nargs=1)
    parser.add_argument("--input", dest="input_channel", default=INPUT_CHANNEL)
    return parser.parse_args()

def main(args=None):
    """Process the ``INPUT_CHANNEL`` redis queue."""
    
    # Parse the command line args.
    if args is None:
        args = parse_args()
    
    # Read the config file.
    config = ConfigParser.SafeConfigParser()
    config.read(args.config_file)
    
    # Setup logging.
    logging.config.fileConfig(args.config_file)
    
    # Patch sockets, threading and the db driver.
    from gevent import monkey
    monkey.patch_all()
    import gevent_psycopg2
    gevent_psycopg2.monkey_patch()
    
    # Bind the model classes.
    engine = create_engine(config.get('app:beliveat', 'sqlalchemy.url'))
    bind_engine(engine)
    
    # Setup the redis queue processor.
    client = get_redis_client()
    processor = QueueProcessor(client, [args.input_channel], handle_data)
    try:
        processor.start()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()

