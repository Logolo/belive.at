<!DOCTYPE HTML>
<html>
  <head>
    <meta charset="utf-8">
    <title>
      BeLive.at
    </title>
    <script src="https://raw.github.com/LearnBoost/socket.io-client/master/dist/socket.io.js"></script>
    <script>
      socket = io.connect('http://localhost:6543/live');
      socket.emit('join', {hello: 'world'});
    </script>
  </head>
  <body>
    <div class="topbar">
      <div class="topbar-inner">
        <div class="container-fluid">
          <a class="brand" href="/">BeLive.at</a>
          <ul class="nav">
            <li>
              <a href="/">${_(u'Index')}</a>
            </li>
            <li>
              <a href="/foo">${_(u'Foo')}</a>
            </li>
            % if request.is_authenticated:
              <li>
                <a href="/users/${request.user.username}">${_(u'Profile')}</a>
              </li>
              <li>
                <a href="/auth/logout">${_(u'Logout')}</a>
              </li>
            % endif
          </ul>
        </div>
      </div>
    </div>
    <div id="main-content" class="container-fluid">
      ${next.body()}
    </div>
  </body>
</html>
