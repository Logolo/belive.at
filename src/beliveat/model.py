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
    

class Assignment(Base, BaseMixin):
    """Encapsulate a assignment."""
    
    __tablename__ = 'assignments'
    
    # Human friendly descriptive information.
    title = Column(Unicode(64))
    description = Column(UnicodeText)
    
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
    
    @property
    def rank(self):
        """"""
        
        n = 0
        
        # for each promote offer within two weeks
            # query = Session.query(PromoteOffer.c)
            # score = 1/max(diff in seconds, 1) * 60*24
            # n += score
        
        # total report offers
            # query = Session.query(ReportOffer.c)
            # score = 3/max(diff in seconds, 1) * 60*24
            # n += score
        
        return n
    
    
    def __json__(self):
        """Return a dictionary representation of the ``Hashtag`` instance.
          
              >>> assignment = Assignment(title='T', description='...')
              >>> assignment.hashtag = Hashtag(value='tag')
              >>> assignment.author = simpleauth_model.User(username='thruflo')
              >>> assignment.__json__()
              {'author': 'thruflo', 'hashtag': 'tag', 'description': '...', 'rank': 0, 'title': 'T'}
              
          
        """
        
        return {
            'title': self.title, 
            'rank': self.rank,
            'description': self.description,
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

class ReportOffer(Base, BaseMixin):
    """Encapsulate an offer to fulfill an assignment."""
    
    __tablename__ = 'report_offers'
    
    note = Column(UnicodeText)
    
    assignment_id = Column(Integer, ForeignKey('assignments.id'))
    assignment = relationship(Assignment, lazy='joined')
    
    user_id = Column(Integer, ForeignKey('auth_users.id'))
    user = relationship(simpleauth_model.User, lazy='joined',
            backref='report_offers')

class PromotionRecord(Base, BaseMixin):
    """"""
    
    __tablename__ = 'promotion_records'
    
    tweet_id = Column(Integer, ForeignKey('tweets.id'))
    tweet = relationship(Tweet, backref='promotion_records')
    
    offer_id = Column(Integer, ForeignKey('promote_offers.id'))
    offer = relationship(PromoteOffer, backref='promotion_records')
    
    # three way code for the action that was taken
    action_code = Column(Integer)


tweets_to_hashtags = Table(
    'tweets_to_hashtags',
    Base.metadata,
    Column('tweet_id', BigInteger, ForeignKey('tweets.id')),
    Column('hashtag_id', Integer, ForeignKey('hashtags.id'))
)
