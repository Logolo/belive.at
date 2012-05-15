# -*- coding: utf-8 -*-

"""Provides FormEncode based validators and schemas."""

import re
from formencode import validators, Invalid, Schema

from ttp import HASHTAG_REGEX as valid_hashtag

ACTION_CODES = (
    (1, 'flag'),
    (3, 'ignore'),
    (5, 'amplify')
)

class Hashtag(validators.UnicodeString):
    """Validates that the user input matches ``valid_hashtag``, strips and
      coerces to lowercase.
      
      If it isn't valid, raises an exception::
      
          >>> Hashtag.to_python('%^Inv@l|d')
          Traceback (most recent call last):
          ...
          Invalid: No spaces or funny characters.
      
      Otherwise strips, coerces to lowercase and returns as unicode::
      
          >>> Hashtag.to_python('Foo')
          u'foo'
      
    """
    
    messages = {'invalid': 'No spaces or funny characters.'}
    
    def _to_python(self, value, state):
        value = super(Hashtag, self)._to_python(value, state)
        return value.strip().lower() if value else value
    
    def validate_python(self, value, state):
        super(Hashtag, self).validate_python(value, state)
        if value:
            candidate = u'#{0}'.format(value)
            if not valid_hashtag.match(candidate):
                msg = self.message("invalid", state)
                raise validators.Invalid(msg, value, state)
    

class ActionCode(validators.Int):
    """Validates that the user input is a valid action code."""
    
    messages = {'invalid': 'Invalid action code.'}
    
    def validate_python(self, value, state):
        super(ActionCode, self).validate_python(value, state)
        if value:
            values = [item[0] for item in ACTION_CODES]
            if not value in values:
                msg = self.message("invalid", state)
                raise validators.Invalid(msg, value, state)
    


class FlexibleSchema(Schema):
    """``formencode.Schema`` that defaults to allow and filter extra fields."""
    
    filter_extra_fields = True
    allow_extra_fields = True

class CreateAssignment(FlexibleSchema):
    """Form fields to validate when creating assignment."""
    
    title = validators.UnicodeString(max=140, not_empty=True)
    description = validators.UnicodeString()

class CreateOffer(FlexibleSchema):
    """Form fields to validate when making an offer to cover or promote an
      assignment.
    """
    
    note = validators.UnicodeString(max=140, if_missing=u'')

class CreateCoverageRecord(FlexibleSchema):
    """Form fields to validate when linked an offer to a tweet."""
    
    tweet_id = validators.Int(not_empty=True)

class CreatePromotionRecord(FlexibleSchema):
    """Form fields to validate when fulfilling an offer to amplify a tweet."""
    
    tweet_id = validators.Int(not_empty=True)
    action_code = ActionCode(not_empty=True)

