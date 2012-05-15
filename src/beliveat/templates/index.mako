<%inherit file="beliveat:templates/layout.mako" />


<div class="container-fluid">
  <div class="row-fluid">
    <img src="${request.static_url('beliveat:assets/gfx/logo.jpg')}" />
    <div style="margin-left: 35px">
      <br />
      <h1>Where you direct the news!</h1>
      <h2>
        Follow a story, suggest ideas and amplify journalists
        working on the ground.
      </h2>
      <p>
        &nbsp;
      </p>
      <div class="span8">
        <h3>
          This is currently a <em>very</em> early pre-ALPHA version.  However,
          you can have a <em>little</em> poke around by selecting one of the
          #Stories below:
        </h3>
        <br />
        <ul class="nav nav-pills" style="zoom: 200%;">
          % for story in stories:
            <li class="active" style="margin-right: 0.5em;">
              <a href="/stories/${story.hashtag.value}">
                #${story.hashtag.value.title()}</a>
            </li>
          % endfor
        </ul>
      </div>
    </div>
  </div>
</div>
