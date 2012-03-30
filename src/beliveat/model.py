# -*- coding: utf-8 -*-

""""""

from sqlalchemy import Column, ForeignKey
from sqlalchemy import DateTime, Integer, Unicode, UnicodeText
from sqlalchemy.orm import backref, relationship

from pyramid_basemodel import Base, BaseMixin, Session, save
from pyramid_simpleauth import model as simpleauth_model
#from pyramid_twitterauth import model as twitterauth_model

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
    


#Offer
#Support

#Match Subscription
#Tweet

#Content Item
