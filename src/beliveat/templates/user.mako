<%inherit file="beliveat:templates/layout.mako" />

% if request.user == request.context:
  ${_(u'Welcome')} ${request.context.username}!
% else:
  ${_(u'This is')} ${request.context.username}!
% endif
