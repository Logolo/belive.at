# -*- coding: utf-8 -*-

""""""

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy import BigInteger, Boolean, DateTime, Integer, Unicode, UnicodeText
from sqlalchemy.orm import backref, relationship

from pyramid_basemodel import Base, BaseMixin, Session, save
from pyramid_simpleauth import model as simpleauth_model
from pyramid_twitterauth import model as twitterauth_model

class Hashtag(Base, BaseMixin):
    """Encapsulate a Twitter #hashtag."""
    
    __tablename__ = 'hashtags'
    
    value = Column(Unicode(32), unique=True)
    
    def __json__(self):
        """Return a dictionary representation of the ``Hashtag`` instance.
          
              >>> tag = Hashtag(value='lolcats')
              >>> tag.__json__()
              {'value': 'lolcats'}
          
        """
        
        return {'value': self.value}
    


class DealStatus(Base, BaseMixin):
    """Lookup table for a ``Deal.status_code``."""
    
    __tablename__ = 'deal_statuses'
    
    code = Column(Integer, unique=True)
    label = Column(Unicode(32))

class Deal(Base, BaseMixin):
    """Encapsulate a deal, aka arrangement, made between users to provide and
      amplify a piece of content.
    """
    
    __tablename__ = 'deals'
    
    # Human friendly descriptive information.
    title = Column(Unicode(64))
    description = Column(UnicodeText)
    
    # Dates this deal is valid for.
    effective_from = Column(DateTime)
    effective_to = Column(DateTime)
    
    # XXX Tracking code, potentially used to identify content coming down the
    # pipe from Twitter.  The idea is the code would be unique to the hashtag
    # this deal belongs to.
    tracking_code = Column(Integer)
    
    # Has a status code.
    status_code = Column(Integer, ForeignKey('deal_statuses.code'))
    status = relationship(DealStatus)
    
    # Belongs to a hashtag.
    hashtag_id = Column(Integer, ForeignKey('hashtags.id'))
    hashtag = relationship(Hashtag, lazy='joined')
    
    # Authored by a user.
    author_id = Column(Integer, ForeignKey('auth_users.id'))
    author = relationship(simpleauth_model.User, lazy='joined')
    
    def __json__(self):
        """Return a dictionary representation of the ``Hashtag`` instance.
          
              >>> deal = Deal(title='T', description='...', tracking_code=123)
              >>> deal.hashtag = Hashtag(value='hashtag')
              >>> deal.author = simpleauth_model.User(username='thruflo')
              >>> deal.__json__()
              {'status': None, 'description': '...', 'author': 'thruflo', 'title': 'T', 'tracking_code': 123, 'hashtag': 'hashtag'}
          
        """
        
        return {
            'title': self.title, 
            'description': self.description,
            'tracking_code': self.tracking_code,
            'status': self.status_code,
            'hashtag': self.hashtag.value,
            'author': self.author.username
        }
    


class Tweet(Base, BaseMixin):
    """Encapsulate a tweet."""
    
    __tablename__ = 'tweets'
    
    id =  Column(BigInteger, primary_key=True)
    
    # ``JSON.dumps`` of the tweet data.
    body = Column(UnicodeText)
    
    # Belongs to a user, through a TwitterAccount.
    user_twitter_id = Column(BigInteger)
    
    # Many to many with Hashtags.
    hashtags = relationship(Hashtag, secondary="tweets_to_hashtags",
            backref="tweets")
    
    def __json__(self):
        """Return a dictionary representation of the ``Tweet`` instance."""
        
        data = json.loads(self.body)
        data['hashtags'] = [item.__json__() for item in self.hashtags]
        return data
    

class TweetRecord(Base, BaseMixin):
    """A record of a RT or a reply."""
    
    __tablename__ = 'tweet_records'
    
    # Should either be a RT or a reply.
    is_retweet = Column(Boolean, default=False)
    is_reply = Column(Boolean, default=False)
    
    tweet_id = Column(BigInteger)
    by_user_twitter_id = Column(BigInteger)


tweets_to_hashtags = Table(
    'tweets_to_hashtags',
    Base.metadata,
    Column('tweet_id', BigInteger, ForeignKey('tweets.id')),
    Column('hashtag_id', Integer, ForeignKey('hashtags.id'))
)

#Offer
#Support

#Match Subscription
#Tweet

#Content Item
