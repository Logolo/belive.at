# Main entry point.
define 'beliveat.main', (exports) ->
    
    init = ->
        view = new beliveat.view.DashboardView el: $ '#dashboard-view'
        live_client = new beliveat.events.LiveSocketClient
    
    exports.init = init

