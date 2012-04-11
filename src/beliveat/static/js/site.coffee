$ ->
    
    # XXX live socket.
    sock = io.connect 'http://localhost:6543/live'
    sock.emit 'join', hello: 'world'
    sock.on 'msg', (data) -> console.log data



