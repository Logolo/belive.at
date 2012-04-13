# Data model.
define 'beliveat.model', (exports) ->
    
    class Assignment extends Backbone.Model
    class AssignmentCollection extends Backbone.Collection
        model: Assignment
    
    class Tweet extends Backbone.Model
    class TweetCollection extends Backbone.Collection
        model: Tweet
    
    exports.Assignment = Assignment
    exports.AssignmentCollection = AssignmentCollection
    exports.Tweet = Tweet
    exports.TweetCollection = TweetCollection

