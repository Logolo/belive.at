<!DOCTYPE HTML>
<html>
  <head>
    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="..." />
    <meta name="author" content="..." />
    <%def name="sub_title()"></%def>
    <title>${self.sub_title()} - ${request.registry.settings['site_title']}</title>
    <link rel="stylesheet" type="text/css" href="${request.static_url('beliveat:assets/base.css')}" />
    <link rel="stylesheet" type="text/css" href="${request.static_url('beliveat:assets/style.css')}" />
    <!-- HTML5 shim, for IE6-8 support of HTML5 elements -->
    <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
    <![endif]-->
  </head>
  <body>
    <div class="navbar navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container-fluid">
          <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </a>
          <a class="brand" href="/">${request.registry.settings['site_title']}</a>
          <div class="nav-collapse">
            <ul class="nav">
              <li>
                <a href="/">${_(u'Index')}</a>
              </li>
              <li>
                <a href="/dashboard">${_(u'Dashboard')}</a>
              </li>
            </ul>
            <ul class="nav pull-right">
              % if request.is_authenticated:
                <li class="dropdown">
                  <a href="#" class="dropdown-toggle"
                      data-toggle="dropdown">
                    ${request.user.username}
                    <b class="caret"></b>
                  </a>
                  <ul class="dropdown-menu">
                    <li>
                      <a href="/users/${request.user.username}">${_(u'Profile')}</a>
                    </li>
                    <li>
                      <a href="/auth/logout">${_(u'Logout')}</a>
                    </li>
                  </ul>
                </li>
              % else:
                <li>
                  <a href="/oauth/twitter/authenticate">${_(u'Signin with Twitter')}</a>
                </li>
              % endif
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div id="main-content" class="container-fluid">
      <div class="row-fluid">
        ${next.body()}
      </div>
      <hr />
      <footer>
        <p>&copy; ...</p>
      </footer>
    </div>
    <script src="//ajax.aspnetcdn.com/ajax/jQuery/jquery-1.7.1.min.js"></script>
    <script src="${request.static_url('beliveat:assets/base.js')}"></script>
    <script src="${request.static_url('beliveat:assets/client.js')}"></script>
  </body>
</html>
