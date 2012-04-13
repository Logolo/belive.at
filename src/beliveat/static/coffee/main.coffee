# Main entry point.
define 'beliveat.main', (exports) ->
    
    init = ->
        new beliveat.view.DashboardView el: $ '#dashboard-view'
        new beliveat.events.LiveSocketClient
    
    exports.init = init

