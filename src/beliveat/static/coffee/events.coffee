# Notifications.
define 'beliveat.events', (exports) ->
    
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
        
    
    exports.dispatcher = dispatcher
    exports.LiveSocketClient = LiveSocketClient

