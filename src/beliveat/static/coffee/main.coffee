# Main entry point.
define 'beliveat.main', (exports) ->
    
    init = ->
        view = new beliveat.view.StoryView el: $ '#story-view'
        live_client = new beliveat.events.LiveSocketClient
    
    exports.init = init

