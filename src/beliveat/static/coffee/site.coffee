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
    
    # Base class for widgets.
    class BaseWidget extends Backbone.View
        initialize: ->
            @model.bind 'change', @render
            @model.bind 'destroy', @remove
            @render()
        
    
    # View for a "normal" assignment listing that's available to promote or cover.
    class AssignmentWidget extends BaseWidget
        # events: 
        render: -> @$el.text 'AssignmentWidget'
    
    # View for an assignment that's been selected to promote.
    class PromoteOfferWidget extends BaseWidget
        # events: 
        render: -> @$el.text 'PromoteOfferWidget'
    
    # View for an assignment that's been selected to cover.
    class CoverOfferWidget extends BaseWidget
        # events: 
        render: -> @$el.text 'CoverOfferWidget'
    
    # View for a tweet that's a candidate to promote.
    class PromoteTweetWidget extends BaseWidget
        # events: 
        render: -> @$el.text 'PromoteTweetWidget'
    
    # View for a tweet that's a candidate to cover an assignment with.
    class CoverTweetWidget extends BaseWidget
        # events: 
        render: -> @$el.text 'CoverTweetWidget'
    
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
                    console.log 'close'
                    $target = @$ '#addAssignmentDetails'
                    $target.slideUp()
                when @states.error
                    console.log 'error'
                    errors = @model.get 'errors'
                    console.log errors
                    # XXX set error on each control group
                when @states.open
                    console.log 'open'
                    $target = @$ '#addAssignmentDetails'
                    $target.slideDown()
                when @states.reset
                    console.log 'reset'
                    $target = @$ 'form'
                    $target[0].reset()
                    @model.set state: @states.close
                when @states.success
                    console.log 'success'
                    alert 'yey!'
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
            @$el.append widget.render().$el.html()
        
    
    # View for the listing of cover offers.
    class CoverOffersListing extends BaseListing
        add: (instance) ->
            widget = new CoverOfferWidget model: instance
            @$el.append widget.render().$el.html()
        
    
    # View for the listing of cover offers.
    class CoverageTweetsListing extends BaseListing
        add: (instance) ->
            widget = new CoverTweetWidget model: instance
            @$el.append widget.$el.html()
        
    
    # View for the listing of promote offers.
    class PromoteOffersListing extends BaseListing
        add: (instance) ->
            widget = new PromoteOfferWidget model: instance
            @$el.append widget.render().$el.html()
        
    
    
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
            # Assignments listing.
            $assignments_el = @$ "#sortedAssignmentsBlock"
            @assignments_listing = new AssignmentsListing
                collection: assignments
                el: $assignments_el
            # Cover offers listing.
            $cover_offers_el = @$ ".pledgedCoverBlock .pledgedCoverWrapper"
            @cover_offers_listing = new CoverOffersListing
                collection: cover_offers
                el: $cover_offers_el
            # Coverage tweets listing.
            $own_tweets_el = @$ ".pledgedCoverBlock .tweetCoverWrapper"
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
    

