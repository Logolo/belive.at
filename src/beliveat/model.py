# -*- coding: utf-8 -*-

"""SQLAlchemy data model."""

import logging
logger = logging.getLogger(__name__)

import json
import datetime
import random

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy import BigInteger, Boolean, DateTime, Integer, Unicode, UnicodeText
from sqlalchemy.orm import backref, relationship

from pyramid_basemodel import Base, BaseMixin, Session, save
from pyramid_simpleauth import model as simpleauth_model
from pyramid_twitterauth import model as twitterauth_model

def generate_public_id():
    return random.randint(100000, 9999999)


class Hashtag(Base, BaseMixin):
    """Encapsulate a Twitter #hashtag."""
    
    __tablename__ = 'hashtags'
    
    value = Column(Unicode(32), unique=True)
    
    @classmethod
    def get_or_create(cls, value):
        """Get or create a Hashtag for the given value."""
        
        hashtag = cls.query.filter_by(value=value).first()
        if not hashtag:
            hashtag = cls(value=value)
        return hashtag
    
    
    def __json__(self):
        """Return a dictionary representation of the ``Hashtag`` instance.
          
              >>> tag = Hashtag(value='lolcats')
              >>> tag.__json__()
              {'value': 'lolcats'}
          
        """
        
        return {'value': self.value}
    

class Assignment(Base, BaseMixin):
    """Encapsulate a assignment."""
    
    __tablename__ = 'assignments'
    
    # Human friendly descriptive information.
    title = Column(Unicode(64))
    description = Column(UnicodeText)
    
    # Public facing unique identifier.
    public_id = Column(Integer, unique=True, default=generate_public_id)
    
    ## Dates this assignment is valid for.
    #effective_from = Column(DateTime)
    #effective_to = Column(DateTime)
    
    # XXX some kind of GEO range / location?
    
    ## Has a status code.
    #status_code = Column(Integer, ForeignKey('assignment_statuses.code'))
    #status = relationship(AssignmentStatus)
    
    content_count = Column(Integer)
    
    # Belongs to a hashtag.
    hashtag_id = Column(Integer, ForeignKey('hashtags.id'))
    hashtag = relationship(Hashtag, lazy='joined')
    
    # Authored by a user.
    author_id = Column(Integer, ForeignKey('auth_users.id'))
    author = relationship(simpleauth_model.User, lazy='joined')
    
    # XXX updated when ``rank`` is calculated.
    promote_offer_count = 0
    cover_offer_count = 0
    
    @property
    def rank(self):
        """Rank by the number of promote and cover offers."""
        
        logger.warn('XXX how do we retire offers?')
        
        # Start with a rank of zero.
        n = 0
        
        now = datetime.datetime.utcnow()
        one_week_ago = now - datetime.timedelta(weeks=1)
        
        # For each promote offer within the last week.
        query = Session.query(PromoteOffer.created)
        query = query.filter(PromoteOffer.assignment==self)
        query = query.filter(PromoteOffer.created>one_week_ago)
        results = query.all()
        self.promote_offer_count = len(results)
        for item in results:
            created_date = item[0]
            delta = now - created_date
            # Make sure the diff is at least one second (n.b.:
            # ``timedelta.total_seconds`` requires Python>=2.7)
            seconds = max(delta.total_seconds(), 1)
            # Half life of 1 day.
            score = 1440 / seconds
            n += score
        
        # For each cover offer within the last week.
        query = Session.query(CoverOffer.created)
        query = query.filter(CoverOffer.assignment==self)
        query = query.filter(CoverOffer.created>one_week_ago)
        results = query.all()
        self.cover_offer_count = len(results)
        for item in results:
            created_date = item[0]
            delta = now - created_date
            seconds = max(delta.total_seconds(), 1)
            # Three times as important as promote offers.
            score = 3 * 1440 / seconds
            n += score
        
        return n
    
    
    def __json__(self):
        """Return a dictionary representation of the ``Assignment`` instance."""
        
        # First calculate the rank.
        rank = self.rank
        
        # That means we can get the counts
        promote_offer_count = self.promote_offer_count
        cover_offer_count = self.cover_offer_count
        
        # Get the profile image.
        twitter_account = self.author.twitter_account
        profile = twitter_account.profile
        data = profile.data
        profile_image = data['profile_image_url']
        
        return {
            'id': self.public_id,
            'author': self.author.username,
            'description': self.description,
            'hashtag': self.hashtag.value,
            'num_promotion_offers': promote_offer_count,
            'num_coverage_offers': cover_offer_count,
            'profile_image_url': profile_image,
            'rank': self.rank,
            'title': self.title 
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
        data['hashtags'] = [item.value for item in self.hashtags]
        return data
    

class TweetRecord(Base, BaseMixin):
    """A record of a RT or a reply."""
    
    __tablename__ = 'tweet_records'
    
    # Should either be a RT or a reply.
    is_retweet = Column(Boolean, default=False)
    is_reply = Column(Boolean, default=False)
    
    tweet_id = Column(BigInteger)
    by_user_twitter_id = Column(BigInteger)

class PromoteOffer(Base, BaseMixin):
    """Encapsulate an offer to promote an assignment."""
    
    __tablename__ = 'promote_offers'
    
    note = Column(UnicodeText)
    
    # XXX n.b.: fill in with the current assignment's count on init.
    promotion_records_count = Column(Integer)
    
    assignment_id = Column(Integer, ForeignKey('assignments.id'))
    assignment = relationship(Assignment, lazy='joined')
    
    user_id = Column(Integer, ForeignKey('auth_users.id'))
    user = relationship(simpleauth_model.User, lazy='joined',
            backref='promote_offers')

class CoverOffer(Base, BaseMixin):
    """Encapsulate an offer to cover an assignment."""
    
    __tablename__ = 'cover_offers'
    
    note = Column(UnicodeText)
    
    assignment_id = Column(Integer, ForeignKey('assignments.id'))
    assignment = relationship(Assignment, lazy='joined')
    
    user_id = Column(Integer, ForeignKey('auth_users.id'))
    user = relationship(simpleauth_model.User, lazy='joined',
            backref='cover_offers')

class PromotionRecord(Base, BaseMixin):
    """"""
    
    __tablename__ = 'promotion_records'
    
    tweet_id = Column(Integer, ForeignKey('tweets.id'))
    tweet = relationship(Tweet, backref='promotion_records')
    
    offer_id = Column(Integer, ForeignKey('promote_offers.id'))
    offer = relationship(PromoteOffer, backref='promotion_records')
    
    # three way code for the action that was taken
    action_code = Column(Integer)

class CoverageRecord(Base, BaseMixin):
    """"""
    
    __tablename__ = 'coverage_records'
    
    tweet_id = Column(Integer, ForeignKey('tweets.id'))
    tweet = relationship(Tweet, backref='coverage_records')
    
    offer_id = Column(Integer, ForeignKey('cover_offers.id'))
    offer = relationship(CoverOffer, backref='coverage_records')


tweets_to_hashtags = Table(
    'tweets_to_hashtags',
    Base.metadata,
    Column('tweet_id', BigInteger, ForeignKey('tweets.id')),
    Column('hashtag_id', Integer, ForeignKey('hashtags.id'))
)
