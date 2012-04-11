# Templates.
define 'beliveat.templates', (exports) ->
    
    example = mobone.string.template """Hello <%~ user['screen_name'] %>"""
    exports.example = example

