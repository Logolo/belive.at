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
    
    # On the left hand side of the page, we have two collections.  First there
    # are your assignments, pinned at the top until you do something with them.  
    # Then below that are the rated assignments from everyone else.
    your_assignments = new AssignmentCollection
    popular_assignments = new AssignmentCollection
    
    # Then on the right hand side, we have the assignments you've offered to
    # cover.  Below that, your tweets flow in until you assign or dismiss them.
    cover_offers = new AssignmentCollection
    own_tweets = new TweetCollection
    
    # Below that, we have the assignments that you've offered to promote, which
    # each individually contain a collection of tweets coming in from other
    # people covering the assignments.
    promote_offers = new AssignmentCollection
    
    
    ### Widgets.
    ###
    
    # Base class for widgets.
    class BaseWidget extends Backbone.View
        initialize: ->
            @model.bind 'change', @render
            @model.bind 'destroy', @remove
            @render()
        
    
    # View for a "normal" assignment listing that's available to promote or cover.
    class AssignmentWidget extends BaseWidget
        # events: 
        render: => @$el.html beliveat.templates.assignment @model.toJSON()
    
    # View for an assignment that's been selected to cover.
    class CoverOfferWidget extends BaseWidget
        # events: 
        render: => @$el.html beliveat.templates.cover_offer @model.toJSON()
    
    # View for a tweet that's a candidate to cover an assignment with.
    class CoverTweetWidget extends BaseWidget
        # events: 
        render: => @$el.html beliveat.templates.cover_tweet @model.toJSON()
    
    # View for an assignment that's been selected to promote.
    class PromoteOfferWidget extends BaseWidget
        # events: 
        render: => @$el.html beliveat.templates.promote_offer @model.toJSON()
    
    # View for a tweet that's a candidate to promote.
    class PromoteTweetWidget extends BaseWidget
        # events: 
        render: => @$el.html beliveat.templates.promote_tweet @model.toJSON()
    
    # View for the create assignment UI.
    class CreateAssignmentWidget extends Backbone.View
        states:
            'close':        'CLOSE'
            'error':        'ERROR'
            'open':         'OPEN'
            'reset':        'RESET'
            'success':      'SUCCESS'
        events:
            'click .close': 'handle_close'
            'focus form':   'handle_focus'
            'submit form':  'handle_submit'
        
        handle_close: => 
            @model.set state: @states.close
            false
        
        handle_focus: =>
            @model.set state: @states.open
        
        handle_submit: =>
            # Get the form data.
            $form = @$ 'form'
            url = $form.attr 'action'
            data = hashtag: @model.get 'hashtag'
            data[item.name] = item.value for item in $form.serializeArray()
            # POST to the server to subscribe.
            $.ajax
                url: url
                data: data
                dataType: "json"
                type: "POST"
                success: (data) =>
                    your_assignments.add data
                    @model.set state: @states.success
                error: (transport) =>
                    data = state: @states.error
                    if transport.status is 400
                        data['errors'] = JSON.parse transport.responseText
                    @model.set data
            # Show the progress indicator.
            @model.set state: @states.progress
            # Squish the original submit event.
            false
        
        render: => 
            state = @model.get 'state'
            # XXX clear any error / success classes.
            switch state
                when @states.close
                    $target = @$ '#addAssignmentDetails'
                    $target.slideUp()
                when @states.error
                    console.log 'error'
                    errors = @model.get 'errors'
                    console.log errors
                    # XXX set error on each control group
                when @states.open
                    $target = @$ '#addAssignmentDetails'
                    $target.slideDown()
                when @states.reset
                    $target = @$ 'form'
                    $target[0].reset()
                    @model.set state: @states.close
                when @states.success
                    @model.set state: @states.reset
        
        initialize: ->
            # Start closed and render when anything changes.
            @model.set state: @states.close
            @model.bind 'change', @render
            @render()
        
    
    
    ### Listings.
    ###
    
    # Base class for listings.
    class BaseListing extends Backbone.View
        initialize: ->
            @collection.bind 'add', (instance) => @add instance
            @collection.bind 'reset', => @collection.each @add
        
    
    # View for the assignments listing.
    class AssignmentsListing extends BaseListing
        add: (instance) ->
            widget = new AssignmentWidget model: instance
            @$el.prepend widget.$el.html()
        
    
    # View for the listing of cover offers.
    class CoverOffersListing extends BaseListing
        add: (instance) ->
            widget = new CoverOfferWidget model: instance
            @$el.prepend widget.$el.html()
        
    
    # View for the listing of cover offers.
    class CoverageTweetsListing extends BaseListing
        add: (instance) ->
            widget = new CoverTweetWidget model: instance
            @$el.prepend widget.$el.html()
        
    
    # View for the listing of promote offers.
    class PromoteOffersListing extends BaseListing
        add: (instance) ->
            widget = new PromoteOfferWidget model: instance
            @$el.prepend widget.$el.html()
        
    
    
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
        handle_tweet_to_promote: (data) ->
            console.log 'DashboardView.handle_tweet_to_promote'
            console.log data
            # XXX broadcast an event using the assignment id.
        
        
        initialize: ->
            # Create assignment widget, passing through the hashtag.
            $create_assignment_el = @$ "#addAssignmentBlock"
            @create_assignment_widget = new CreateAssignmentWidget
                el: $create_assignment_el
                model: new Backbone.Model
                    hashtag: @hashtag
            # Assignments listings.
            $your_assignments_el = @$ "#yourAssignmentsBlock ul"
            $popular_assignments_el = @$ "#sortedAssignmentsBlock ul"
            @your_assignments_listing = new AssignmentsListing
                collection: your_assignments
                el: $your_assignments_el
            @popular_assignments_listing = new AssignmentsListing
                collection: popular_assignments
                el: $popular_assignments_el
            # Cover offers and own tweets listings.
            $cover_offers_el = @$ ".pledgedCoverBlock .pledgedCoverWrapper"
            $own_tweets_el = @$ ".pledgedCoverBlock .tweetCoverWrapper"
            @cover_offers_listing = new CoverOffersListing
                collection: cover_offers
                el: $cover_offers_el
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
            dispatcher.on "tweet_to_promote:#{@hashtag}", @handle_tweet_to_promote
        
    
    # XXX temporary init code.
    $target = $ '#dashboard-view'
    dashboard_view = new DashboardView el: $target
    

