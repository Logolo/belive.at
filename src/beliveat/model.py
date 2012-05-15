# -*- coding: utf-8 -*-

"""SQLAlchemy data model and traversal factories."""

import logging
logger = logging.getLogger(__name__)

import json
import datetime
import random

from formencode import validators, Invalid

from sqlalchemy import event, not_
from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy import BigInteger, Boolean, DateTime, Integer, Unicode, UnicodeText
from sqlalchemy.orm import backref, relationship

from pyramid.security import ALL_PERMISSIONS
from pyramid.security import Allow, Deny
from pyramid.security import Authenticated, Everyone

from zope.interface import implements

from pyramid_basemodel import Base, BaseMixin, Session, save
from pyramid_simpleauth import model as simpleauth_model
from pyramid_twitterauth import model as twitterauth_model

from .events import StoryAdded
from .interfaces import IOffer, IOfferRoot, IOfferRecord
from .schema import Hashtag as ValidHashtag

def generate_public_id():
    return random.randint(10000, 99999999)

def get_one_week_ago():
    now = datetime.datetime.utcnow()
    return now - datetime.timedelta(weeks=1)


class Root(object):
    """Root object of the application's resource tree."""
    
    __name__ = None
    
    __acl__ = [
        (Allow, 'r:admin', ALL_PERMISSIONS),
        (Allow, Authenticated, 'view'),
        (Deny, Everyone, ALL_PERMISSIONS),
    ]
    
    def __init__(self, request):
        self.request = request
    
    def __getitem__(self, key):
        raise KeyError
    

class StoryRoot(Root):
    """Root object of the story resource tree."""
    
    __name__ = 'stories'
    
    @property
    def __parent__(self):
        return Root(self.request)
    
    @property
    def model_cls(self):
        return Story
    
    def __getitem__(self, key, validator_cls=None, model_cls=None):
        """Lookup the context by matching the ``key`` against the story's
          hashtag value.
        """
        
        logger.debug('{0}: {1}'.format(self.__class__.__name__, key))
        
        # Test jig.
        if validator_cls is None:
            validator_cls = ValidHashtag
        if model_cls is None:
            model_cls = self.model_cls
        
        # Lookup the context by hashtag value.
        try:
            value = validator_cls.to_python(key)
        except Invalid:
            pass
        else:
            hashtag = Hashtag.get_or_create(value)
            context = model_cls.query.filter_by(hashtag=hashtag).first()
            # XXX if the story doesn't exist, create it.
            if not context:
                context = model_cls(hashtag=hashtag)
                event = StoryAdded(self.request, context)
                self.request.registry.notify(event)
                save(context)
            return context
        raise KeyError
    

class AssignmentRoot(StoryRoot):
    """Traversal root for a story's assignments."""
    
    __name__ = 'assignments'
    
    @property
    def __parent__(self):
        return self.story.public_id
    
    @property
    def model_cls(self):
        return Assignment
    
    def __init__(self, story):
        self.story = story
    
    def __getitem__(self, key, validator_cls=None, model_cls=None):
        """Lookup the context by model_cls and public id."""
        
        logger.debug('{0}: {1}'.format(self.__class__.__name__, key))
        
        # Test jig.
        if validator_cls is None:
            validator_cls = validators.Int
        if model_cls is None:
            model_cls = self.model_cls
        
        # Lookup the context by hashtag value.
        try:
            value = validator_cls.to_python(key)
        except Invalid:
            pass
        else:
            context = model_cls.get_by_public_id(value)
            logger.warn(context)
            if context:
                return context
        raise KeyError
    

class BaseOfferRoot(AssignmentRoot):
    """Traversal lookup for an assignment's offers."""
    
    @property
    def __parent__(self):
        return self.assignment.public_id
    
    def __init__(self, assignment):
        self.assignment = assignment
    
    model_cls = NotImplemented

class CoverOfferRoot(BaseOfferRoot):
    """Traversal lookup for an assignment's cover offers."""
    
    implements(IOfferRoot)
    
    __name__ = 'cover_offers'
    
    @property
    def model_cls(self):
        return CoverOffer
    

class PromoteOfferRoot(BaseOfferRoot):
    """Traversal lookup for an assignment's promote offers."""
    
    implements(IOfferRoot)
    
    __name__ = 'promote_offers'
    
    @property
    def model_cls(self):
        return PromoteOffer
    

class TweetRoot(Root):
    """Root object of the tweet resource tree."""
    
    __name__ = 'tweets'
    
    @property
    def __parent__(self):
        return Root(self.request)
    
    def __getitem__(self, key, validator_cls=None, model_cls=None):
        """Lookup a tweet by status id."""
        
        logger.debug('{0}: {1}'.format(self.__class__.__name__, key))
        
        # Test jig.
        if validator_cls is None:
            validator_cls = validators.Int
        if model_cls is None:
            model_cls = Tweet
        
        # Lookup the context by id.
        try:
            value = validator_cls.to_python(key)
        except Invalid:
            pass
        else:
            context = model_cls.query.get(value)
            if context:
                return context
        raise KeyError
    


class PublicIdMixin(object):
    """Provides a ``public_id`` property and a ``get_by_public_id`` classmethod."""
    
    # Public facing unique identifier.
    public_id = Column(Integer, unique=True, default=generate_public_id)
    
    @classmethod
    def get_by_public_id(cls, public_id):
        """Return an instance if it matches ``public_id``."""
        
        query = cls.query.filter_by(public_id=public_id) 
        return query.first()
    


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
    

class Story(Base, BaseMixin, PublicIdMixin):
    """A story that people are following."""
    
    __tablename__ = 'stories'
    
    @property
    def __parent__(self):
        return StoryRoot(None)
    
    @property
    def __name__(self):
        return self.hashtag.value
    
    @property
    def __acl__(self):
        return [
            (Allow, 'r:admin', ALL_PERMISSIONS),
            (Allow, Authenticated, 'view'),
            (Deny, Everyone, ALL_PERMISSIONS),
        ]
    
    def __getitem__(self, key):
        """A story is a traversal container for assignments."""
        
        logger.debug('{0}: {1}'.format(self.__class__.__name__, key))
        
        if key == 'assignments':
            return AssignmentRoot(self)
        raise KeyError
    
    
    # Belongs to a hashtag.
    hashtag_id = Column(Integer, ForeignKey('hashtags.id'))
    hashtag = relationship(Hashtag, lazy='joined', backref='story')
    
    def touch(self):
        """Touch the modified date of this story."""
        
        self.modified = datetime.datetime.utcnow()
        save(self)
    
    def __json__(self):
        """Return a dictionary representation of the ``Story`` instance."""
        
        return {
            'id': self.public_id,
            'hashtag': self.hashtag.value
        }
    

class Assignment(Base, BaseMixin, PublicIdMixin):
    """Encapsulate a assignment."""
    
    __tablename__ = 'assignments'
    
    @property
    def __parent__(self):
        return AssignmentRoot(self.story)
    
    @property
    def __name__(self):
        return self.public_id
    
    @property
    def __acl__(self):
        return [
            (Allow, 'r:admin', ALL_PERMISSIONS),
            (Allow, Authenticated, 'view'),
            (Allow, self.author.canonical_id, 'edit'),
            (Deny, Everyone, ALL_PERMISSIONS),
        ]
    
    def __getitem__(self, key):
        """An assignment is a traversal container for offers."""
        
        logger.debug('{0}: {1}'.format(self.__class__.__name__, key))
        
        if key == 'promote_offers':
            return PromoteOfferRoot(self)
        elif key == 'cover_offers':
            return CoverOfferRoot(self)
        raise KeyError
    
    
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
    
    content_count = Column(Integer, default=0)
    
    # Belongs to a story.
    story_id = Column(Integer, ForeignKey('stories.id'))
    story = relationship(Story, lazy='joined')
    
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
        
        # Start with a rank of zero and ignore everything that's over a week old.
        n = 0
        now = datetime.datetime.utcnow()
        one_week_ago = get_one_week_ago()
        
        # For each promote offer.
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
            if hasattr(delta, 'total_seconds'):
                tot_seconds = delta.total_seconds()
            else:
                secs = delta.seconds + delta.days * 24.0 * 3600.0
                tot_seconds = (delta.microseconds + secs * 10.0**6) / 10.0**6
            seconds = max(tot_seconds, 1)
            # Half life of 1 day.
            score = 1440 / seconds
            n += score
        
        # For each cover offer.
        query = Session.query(CoverOffer.created)
        query = query.filter(CoverOffer.assignment==self)
        query = query.filter(CoverOffer.created>one_week_ago)
        results = query.all()
        self.cover_offer_count = len(results)
        for item in results:
            created_date = item[0]
            delta = now - created_date
            if hasattr(delta, 'total_seconds'):
                tot_seconds = delta.total_seconds()
            else:
                secs = delta.seconds + delta.days * 24.0 * 3600.0
                tot_seconds = (delta.microseconds + secs * 10.0**6) / 10.0**6
            seconds = max(tot_seconds, 1)
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
            'story': self.story.hashtag.value,
            'num_promotion_offers': promote_offer_count,
            'num_coverage_offers': cover_offer_count,
            'profile_image_url': profile_image,
            'rank': self.rank,
            'title': self.title,
            # Default flags -- overriden by the view machinery.
            'covering': False,
            'promoting': False
        }
    

class Tweet(Base, BaseMixin):
    """Encapsulate a tweet."""
    
    __tablename__ = 'tweets'
    
    @property
    def __parent__(self):
        return TweetRoot(None)
    
    @property
    def __name__(self):
        return self.id
    
    @property
    def __acl__(self, user_cls=None, account_cls=None):
        """Grant all permissions to the Tweet's author, if found."""
        
        # Test jig.
        if user_cls is None:
            user_cls = simpleauth_model.User
        if account_cls is None:
            account_cls = twitterauth_model.TwitterAccount
        
        # Start with the standard ACL.
        policy = [
            (Allow, 'r:admin', ALL_PERMISSIONS),
            (Allow, Authenticated, 'view'),
            (Deny, Everyone, ALL_PERMISSIONS),
        ]
        
        # If we can find the tweet's author, insert a line that
        # grants them edit permission.
        twitter_id = self.user_twitter_id
        query = user_cls.query.filter(account_cls.twitter_id==twitter_id)
        user = query.first()
        if user:
            policy.insert(2, (Allow, user.canonical_id, 'edit'))
        
        # Return the policy.
        return policy
    
    
    id = Column(BigInteger, primary_key=True)
    
    # ``JSON.dumps`` of the tweet data.
    body = Column(UnicodeText)
    
    # Belongs to a user, through a TwitterAccount.
    user_twitter_id = Column(BigInteger)
    
    # Many to many with Hashtags.
    hashtags = relationship(Hashtag, secondary="tweets_to_hashtags",
            backref="tweets")
    
    # Has the originating user hidden this?
    hidden = Column(Boolean, default=False)
    
    def __json__(self):
        """Return a dictionary representation of the ``Tweet`` instance."""
        
        data = json.loads(self.body)
        data['hashtags'] = [item.value for item in self.hashtags]
        if self.coverage_record:
            data['coverage_record'] = self.coverage_record.__json__()
        return data
    

class TweetRecord(Base, BaseMixin):
    """A record of a RT or a reply."""
    
    __tablename__ = 'tweet_records'
    
    # Should either be a RT or a reply.
    is_retweet = Column(Boolean, default=False)
    is_reply = Column(Boolean, default=False)
    
    tweet_id = Column(BigInteger)
    by_user_twitter_id = Column(BigInteger)

class PromoteOffer(Base, BaseMixin, PublicIdMixin):
    """Encapsulate an offer to promote an assignment."""
    
    implements(IOffer)
    
    __tablename__ = 'promote_offers'
    
    @property
    def __parent__(self):
        return PromoteOfferRoot(self.assignment)
    
    @property
    def __name__(self):
        return self.public_id
    
    @property
    def __acl__(self):
        return [
            (Allow, 'r:admin', ALL_PERMISSIONS),
            (Allow, Authenticated, 'view'),
            (Allow, self.user.canonical_id, 'edit'),
            (Deny, Everyone, ALL_PERMISSIONS),
        ]
    
    def __getitem__(self, key):
        logger.debug('{0}: {1}'.format(self.__class__.__name__, key))
        raise KeyError
    
    
    note = Column(UnicodeText)
    
    # XXX n.b.: fill in with the current assignment's count on init.
    promotion_records_count = Column(Integer)
    
    assignment_id = Column(Integer, ForeignKey('assignments.id'))
    assignment = relationship(Assignment, lazy='joined')
    
    user_id = Column(Integer, ForeignKey('auth_users.id'))
    user = relationship(simpleauth_model.User, lazy='joined',
            backref='promote_offers')
    
    # Has the originating user closed this?
    closed = Column(Boolean, default=False)
    
    def get_pending_tweets(self, tweet_cls=None, record_cls=None, offer_cls=None):
        """Return the tweets that have been flagged as covering this offer's
          assignment and that haven't been 'deal with' already.
        """
        
        # Test jig.
        if tweet_cls is None:
            tweet_cls = Tweet
        if record_cls is None:
            record_cls = CoverageRecord
        if offer_cls is None:
            offer_cls = CoverOffer
        
        # Shortcut if closed.
        if self.closed:
            return []
        
        # Get the tweets that are related to cover offers made on this promote
        # offer's assignment.
        query = tweet_cls.query.join(tweet_cls.coverage_record, record_cls.offer)
        query = query.filter(offer_cls.assignment==self.assignment)
        # That haven't already been dealt with.
        dealt_with = [item.tweet_id for item in self.promotion_records]
        query = query.filter(not_(tweet_cls.id.in_(dealt_with)))
        return query.all()
    
    def __json__(self):
        """Return a dictionary representation of the ``PromoteOffer`` instance."""
        
        pending_tweets = self.get_pending_tweets()
        return {
            'id': self.public_id,
            'offer_type': 'promote',
            'note': self.note,
            'assignment': self.assignment.public_id,
            'story': self.assignment.story.hashtag.value,
            'title': self.assignment.title,
            'user': self.user.username,
            'closed': self.closed,
            'tweets': [item.__json__() for item in pending_tweets]
        }
    

class CoverOffer(Base, BaseMixin, PublicIdMixin):
    """Encapsulate an offer to cover an assignment."""
    
    implements(IOffer)
    
    __tablename__ = 'cover_offers'
    
    @property
    def __parent__(self):
        return CoverOfferRoot(self.assignment)
    
    @property
    def __name__(self):
        return self.public_id
    
    @property
    def __acl__(self):
        acl = [
            (Allow, 'r:admin', ALL_PERMISSIONS),
            (Allow, Authenticated, 'view'),
            (Allow, self.user.canonical_id, 'edit'),
            (Deny, Everyone, ALL_PERMISSIONS),
        ]
        logger.debug(acl)
        return acl
    
    def __getitem__(self, key):
        logger.debug('{0}: {1}'.format(self.__class__.__name__, key))
        raise KeyError
    
    
    note = Column(UnicodeText)
    
    assignment_id = Column(Integer, ForeignKey('assignments.id'))
    assignment = relationship(Assignment, lazy='joined')
    
    user_id = Column(Integer, ForeignKey('auth_users.id'))
    user = relationship(simpleauth_model.User, lazy='joined',
            backref='cover_offers')
    
    # Has the originating user closed this?
    closed = Column(Boolean, default=False)
    
    def __json__(self):
        """Return a dictionary representation of the ``CoverOffer`` instance."""
        
        return {
            'id': self.public_id,
            'offer_type': 'cover',
            'note': self.note,
            'assignment': self.assignment.public_id,
            'story': self.assignment.story.hashtag.value,
            'title': self.assignment.title,
            'user': self.user.username,
            'closed': self.closed
        }
    

class PromotionRecord(Base, BaseMixin):
    """"""
    
    implements(IOfferRecord)
    
    __tablename__ = 'promotion_records'
    
    tweet_id = Column(BigInteger, ForeignKey('tweets.id'))
    tweet = relationship(Tweet, backref='promotion_records')
    
    offer_id = Column(Integer, ForeignKey('promote_offers.id'))
    offer = relationship(PromoteOffer, backref='promotion_records')
    
    # three way code for the action that was taken
    action_code = Column(Integer)
    
    def __json__(self):
        return {
            'action': self.action_code,
            'offer': self.offer.__json__(),
            'tweet': self.tweet_id
        }
    

class CoverageRecord(Base, BaseMixin):
    """"""
    
    implements(IOfferRecord)
    
    __tablename__ = 'coverage_records'
    
    tweet_id = Column(BigInteger, ForeignKey('tweets.id'))
    tweet = relationship(Tweet, lazy='joined', uselist=False,
            backref=backref('coverage_record', lazy='joined', uselist=False))
    
    offer_id = Column(Integer, ForeignKey('cover_offers.id'))
    offer = relationship(CoverOffer, uselist=False, backref='coverage_records')
    
    def __json__(self):
        return {
            'offer': self.offer.__json__(),
            'tweet': self.tweet_id
        }
    


tweets_to_hashtags = Table(
    'tweets_to_hashtags',
    Base.metadata,
    Column('tweet_id', BigInteger, ForeignKey('tweets.id')),
    Column('hashtag_id', Integer, ForeignKey('hashtags.id'))
)

# Immediately set ``public_id`` on new story, assignment and offer instances when
# first created (n.b.: init is not triggered when loaded from the db).
def set_public_id(instance, *args, **kwargs):
    """Set ``instance.public_id`` if not provided in the ``kwargs``.
      
      Setup::
      
          >>> from mock import Mock
          >>> mock_instance = Mock()
          >>> mock_instance.public_id = None
      
      Test::
      
          >>> set_public_id(mock_instance, public_id=1234)
          >>> mock_instance.public_id
          >>> set_public_id(mock_instance)
          >>> int(mock_instance.public_id) == mock_instance.public_id
          True
      
    """
    
    if not kwargs.has_key('public_id'):
        instance.public_id = generate_public_id()

for cls in (Story, Assignment, PromoteOffer, CoverOffer):
    event.listen(cls, 'init', set_public_id)

