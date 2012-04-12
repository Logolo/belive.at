$ ->
    
    # Global event dispatcher.
    dispatcher = _.clone Backbone.Events
    
    # Model classes.
    class Assignment extends Backbone.Model
    class AssignmentCollection extends Backbone.Collection
        model: Assignment
    
    class Tweet extends Backbone.Model
    class TweetCollection extends Backbone.Collection
        model: Tweet
    
    # ...
    class DashboardView extends Backbone.View
        
        # XXX hardcoded.
        hashtag: 'syria'
        
        handle_own_tweet: (data) ->
            console.log 'Dashboard.handle_tweet'
            console.log data
            console.log beliveat.templates.example data
        
        start_listening: ->
            dispatcher.on "own_tweet:#{@hashtag}", @handle_own_tweet
            # ... more events
        
        initialize: ->
            @promote_assignments = new AssignmentCollection
            @cover_assignments = new AssignmentCollection
            @assignments = new AssignmentCollection
            @start_listening()
        
    
    # Consume and re-broadcast socket.io notifications.
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
        
    
    dashboard_view = new DashboardView
    live_client = new LiveSocketClient
    

