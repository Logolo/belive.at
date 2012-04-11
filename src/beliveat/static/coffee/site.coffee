$ ->
    
    # XXX live socket.
    sock = io.connect 'http://localhost:6543/live'
    sock.emit 'join', hello: 'world'
    sock.on 'tweet', (data) -> 
        console.log 'GOT A TWEET'
        console.log typeof data
        console.log data
    
    

