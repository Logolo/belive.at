$ ->
    
    # Event dispatcher.
    dispatcher = _.clone Backbone.Events
    
    # Socket.io client.
    class LiveSocketClient 
        # Re-broadcast notifications locally, using the event type and
        # hashtag as the event name.
        dispatch: (event_name, hashtag, data_str) ->
            data = JSON.parse data_str
            dispatcher.trigger "#{event_name}:#{hashtag}", data
        
        # Bind to notifications
        constructor: ->
            @sock = io.connect '/live'
            @sock.emit 'join', status: 'ready'
            @sock.on 'notification', @dispatch
        
    
    live_client = new LiveSocketClient
    
    # Data model.
    class Assignment extends Backbone.Model
    class AssignmentCollection extends Backbone.Collection
        model: Assignment
    
    class Tweet extends Backbone.Model
    class TweetCollection extends Backbone.Collection
        model: Tweet
    
    assignments = new AssignmentCollection
    cover_offers = new AssignmentCollection
    promote_offers = new AssignmentCollection
    own_tweets = new TweetCollection
    
    ### Widgets.
    ###
    
    # View for a "normal" assignment listing that's available to promote or cover.
    class AssignmentWidget extends Backbone.View
        # events: 
        render: -> @$el.text 'AssignmentWidget'
        render: -> @$el.text 'AssignmentWidget'
        initialize: ->
            @model.bind 'change', @render
            @model.bind 'destroy', @remove
        
    
    # View for an assignment that's been selected to promote.
    class PromoteOfferWidget extends Backbone.View
        # events: 
        render: -> @$el.text 'PromoteOfferWidget'
    
    # View for an assignment that's been selected to cover.
    class CoverOfferWidget extends Backbone.View
        # events: 
        render: -> @$el.text 'CoverOfferWidget'
    
    # View for a tweet that's a candidate to promote.
    class PromoteTweetWidget extends Backbone.View
        # events: 
        render: -> @$el.text 'PromoteTweetWidget'
    
    # View for a tweet that's a candidate to cover an assignment with.
    class CoverTweetWidget extends Backbone.View
        # events: 
        render: -> @$el.text 'CoverTweetWidget'
    
    # View for the create assignment UI.
    class CreateAssignmentWidget extends Backbone.View
        # events: 
        render: -> # pass
    
    
    ### Listings.
    ###
    
    # View for the assignments listing.
    class AssignmentsListing extends Backbone.View
        add: (instance) ->
            widget = new AssignmentWidget model: instance
            @el.append widget.$el.html()
        
        initialize: ->
            @collection.bind 'add', @add
            @collection.bind 'reset', => @collection.each @add
        
    
    # View for the listing of cover offers.
    class CoverOffersListing extends Backbone.View
        add: (instance) ->
            widget = new CoverOfferWidget model: instance
            @el.append widget.$el.html()
        
        initialize: ->
            @collection.bind 'add', @add
            @collection.bind 'reset', => @collection.each @add
        
    
    # View for the listing of cover offers.
    class CoverageTweetsListing extends Backbone.View
        add: (instance) ->
            widget = new CoverTweetWidget model: instance
            @el.append widget.$el.html()
        
        initialize: ->
            @collection.bind 'add', @add
            @collection.bind 'reset', => @collection.each @add
        
    
    # View for the listing of promote offers.
    class PromoteOffersListing extends Backbone.View
        add: (instance) ->
            widget = new PromoteOfferWidget model: instance
            @el.append widget.$el.html()
        
        initialize: ->
            @collection.bind 'add', @add
            @collection.bind 'reset', => @collection.each @add
        
    
    
    ### Pages.
    ###
    
    # View for the #hashtag dashboard, currently hardcoded to #syria.
    class DashboardView extends Backbone.View
        
        # XXX hardcoded for now.
        hashtag: 'syria'
        
        # Handle the arrival of a tweet that's a candidate to be used to cover
        # an assignment.
        handle_own_tweet: (data) ->
            console.log 'DashboardView.handle_tweet'
            own_tweets.add(data)
        
        # Handle the arrival of a tweet that's been verified by its author as
        # coverage of an assignment this use has offered to promote.
        handle_coverage: (data) ->
            console.log 'DashboardView.handle_coverage'
            console.log data
            # XXX broadcast an event using the assignment id.
        
        
        initialize: ->
            # Create assignment widget.
            $create_assignment_el = @$ "#addAssignmentBlock"
            @create_assignment_widget = new CreateAssignmentWidget
                el: $create_assignment_el
            # Assignments listing.
            $assignments_el = @$ "#sortedAssignmentsBlock"
            @assignments_listing = new AssignmentsListing
                collection: assignments
                el: $assignments_el
            # Cover offers listing.
            $cover_offers_el = @$ "#pledgedCoverageBlock .pledgedCoverWrapper"
            @cover_offers_listing = new CoverOffersListing
                collection: cover_offers
                el: $cover_offers_el
            # Coverage tweets listing.
            $own_tweets_el = @$ "#pledgedCoverageBlock .tweetCoverWrapper"
            @own_tweets_listing = new CoverageTweetsListing
                collection: own_tweets
                el: $own_tweets_el
            # Promote offers listing.
            $promote_offers_el = @$ "#pledgedRetweetBlock"
            @promote_offers_listing = new PromoteOffersListing
                collection: promote_offers
                el: $promote_offers_el
            # Bind to socket notifications.
            dispatcher.on "own_tweet:#{@hashtag}", @handle_own_tweet
            dispatcher.on "coverage:#{@hashtag}", @handle_coverage
        
    
    # XXX temporary init code.
    $target = $ '#dashboard-view'
    dashboard_view = new DashboardView el: $target
    

