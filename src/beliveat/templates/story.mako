<%inherit file="beliveat:templates/layout.mako" />

<%def name="sub_title()">
  #${request.context.hashtag.value}
</%def>

<%def name="sub_scripts()">
  <script src="${request.static_url('beliveat:assets/client.js')}"></script>
  <script type="text/javascript">
    //<![CDATA[
    // Tell the client who the authenticated user is and which hashtag we're on.
    beliveat.user = '${request.user.username}';
    beliveat.story = '${request.context.hashtag.value}';
    // Bootstrap the data model.
    beliveat.model.your_assignments = new beliveat.model.AssignmentCollection();
    beliveat.model.your_assignments.reset(${your_assignments.replace('</', '<\/') | n});
    beliveat.model.popular_assignments = new beliveat.model.AssignmentCollection();
    beliveat.model.popular_assignments.reset(${popular_assignments.replace('</', '<\/') | n});
    beliveat.model.cover_offers = new beliveat.model.AssignmentCollection();
    beliveat.model.cover_offers.reset(${cover_offers.replace('</', '<\/') | n});
    beliveat.model.own_tweets = new beliveat.model.TweetCollection();
    beliveat.model.own_tweets.reset(${own_tweets.replace('</', '<\/') | n});
    beliveat.model.promote_offers = new beliveat.model.AssignmentCollection();
    beliveat.model.promote_offers.reset(${promote_offers.replace('</', '<\/') | n});
    // start the client running
    beliveat.main.init()
    //]]>
  </script>
</%def>

<%def name="tweetCover()">
  <div class="tweetCover">
    <div class="tweetCoverLink">
      <a src="#YouTubeLink">
        <img src="http://img.youtube.com/vi/qVaW3rfCwq8/0.jpg" />
      </a>
    </div>
    <div class="tweetText">
      <h3>"YouTube video title here"</h3>
      <p>Tweet from the person promoting the video is here. Blah blah blah blah. Blah!</p>
      <div class="tweetButtons">
        <div class="btn-group buttonLink">
          <a class="btn dropdown-toggle btn-primary" data-toggle="dropdown" href="#">
            Link to Assignment
            <span class="caret"></span>
          </a>
          <ul class="dropdown-menu">
            <!-- dropdown menu links - iterate through COVER_PLEDGES -->
            <li><a href="#">Cover Pledge #1</a></li>
            <li><a href="#">Cover Pledge #2</a></li>
            <li><a href="#">Cover Pledge #3</a></li>
          </ul>
        </div>
        <button class="buttonHide">Hide</button>        
      </div>
    </div>
    <div class="clear"></div>
  </div>
</%def>

<%def name="tweetCoverOpened()">
  <div class="tweetPromoteOpened">
      <button class="btn-mini buttonTweetViewClose">x</button>
      <h3>"YouTube video title here"</h3>
    <div class="videoWrapper">
      <iframe class="youtube-player" type="text/html" src="http://www.youtube.com/embed/qVaW3rfCwq8" frameborder="0"width="640" height="384"></iframe>
    </div>
      <div class="tweetButtons">
        <div class="btn-group buttonLink">
          <a class="btn dropdown-toggle btn-primary" data-toggle="dropdown" href="#">
            Link to Assignment
            <span class="caret"></span>
          </a>
          <ul class="dropdown-menu">
            <!-- dropdown menu links - iterate through COVER_PLEDGES -->
            <li><a href="#">Cover Pledge #1</a></li>
            <li><a href="#">Cover Pledge #2</a></li>
            <li><a href="#">Cover Pledge #3</a></li>
          </ul>
        </div>
        <button class="buttonHide">Hide</button>        
      </div>
    <div class="clear"></div>
  </div>
</%def>

<%def name="tweetPromote()">
  <div class="tweetPromote">
    <div class="tweetPromoteLink">
      <a src="#YouTubeLink">
        <img src="http://img.youtube.com/vi/qVaW3rfCwq8/0.jpg" />
      </a>
    </div>    
    <div class="tweetText">
      <img src="/static/gfx/defaultUser.png" />
      <h3>"YouTube video title here"</h3>
      <p>Tweet from the person promoting the video is here. Blah blah blah blah. Blah!</p>
      <div class="tweetButtons">
        <button class="buttonFlag"><img src="/static/gfx/flag.png" />Flag as Inappropriate</button>
        <button class="buttonRetweet btn-primary">Retweet</button>        
        <button class="buttonHide">Hide</button>
      </div>
    </div>
    <div class="clear"></div>
  </div>
</%def>

<%def name="tweetPromoteOpened()">
  <div class="tweetPromoteOpened">
      <button class="btn-mini buttonTweetViewClose">x</button>
      <h3>"YouTube video title here"</h3>
    <div class="videoWrapper">
      <iframe class="youtube-player" type="text/html" src="http://www.youtube.com/embed/qVaW3rfCwq8" frameborder="0"width="640" height="384"></iframe>
    </div>
    <div class="tweetButtons">
      <button class="buttonFlag"><img src="/static/gfx/flag.png" />Flag as Inappropriate</button>
      <button class="buttonRetweet btn-primary">Retweet</button>        
      <button class="buttonHide">Hide</button>
    </div>
    <div class="clear"></div>
  </div>
</%def>

<%def name="pledgedCover()">
  <div class="pledgedCover">
    <div class="pledgedCoverBody">
      <div class="pledgedCoverClose">
         <button class="btn-mini buttonCoverClose">x</button>
      </div>
      <div class="pledgedCoverTitle">"Film the awesome blah, blah blah."</div>
      <div class="pledgedCoverIcon">
        <img src="/static/gfx/cover-icon.png" />
      </div>
    </div>
    <div class="clear"></div>
    <div class="pledgedCoverStatus">You pledged to cover this.</div>
  </div>
</%def>

<%def name="pledgedPromote()">
  <div class="pledgedPromote">
    <div class="pledgedPromoteBody">
      <div class="pledgedPromoteIcon"><img src="/static/gfx/promote-icon.png" /></div>
      <div class="pledgedPromoteTitle">"Get footage of nuclear waste train next to church."</div>
      <div class="pledgedPromoteClose">
         <button class="btn-mini buttonPromoteClose">x</button>
      </div>
    </div>
    <div class="clear"></div>
    <div class="pledgedPromoteStatus">You pledged to promote this.</div>
  </div>
</%def>


<div id="story-view">
  <h1>#${request.context.hashtag.value}</h1>
  <div class="container-fluid">
    <div class="row-fluid">
      <div id="assignmentColumn" class="span6">
        <h3 class="columnTitle">Assignments</h3>
        <div id="addAssignmentBlock">
          <form action="${request.resource_url(request.context, 
                  'assignments', '@@create')}"
              method="post">
            <fieldset>
              <div class="control-group">
                <div id="addAssignmentTitle" class="controls">
                  <input type="text" name="title"
                      placeholder="+ Add a new assignment"
                  />
                  <span class="help-inline"></span>
                </div>
              </div>
              <div id="addAssignmentDetails">
                <div class="control-group">
                  <label for="formAddAssignmentDetail" class="control-label">
                    Please give any relevant details, context, location, time, etc.
                  </label>
                  <div id="addAssignmentDescription" class="controls">
                    <textarea name="description" rows="5"></textarea>
                    <span class="help-inline"></span>
                  </div>
                </div>
                <div class="form-actions">
                  <input id="addAssignmentSubmit" type="submit" class="btn btn-primary"
                      value="Submit"
                  />
                  <a class="btn close" href="#close">Close</a>
                </div>
              </div>
            </fieldset>
          </form>
        </div>  
        <div id="yourAssignmentsBlock">
          <h4>Your Assignments</h4>
          <ul></ul>
        </div>
        <div id="sortedAssignmentsBlock">
          <h4>Popular Assignments</h4>
          <ul></ul>
        </div>
      </div>
      <div id="coverageColumn" class="span6">
        <h3 class="columnTitle">Coverage</h3>
        <h4>Reporting</h4>
        <div class="pledgedCoverBlock">
          <div class="pledgedCoverWrapper">
            <%doc>
              ${self.pledgedCover()}
              ${self.pledgedCover()}
            </%doc>
          </div>
          <div class="tweetCoverWrapper">
            <%doc>
              ${self.tweetCoverOpened()}
              ${self.tweetCover()}
            </%doc>
          </div>
        </div>
        <h4>Amplifying</h4>
        <div class="pledgedPromoteBlock">
          <div class="pledgedPromoteWrapper">
            <%doc>
              ${pledgedPromote()}
              <div class="tweetPromoteWrapper">
                ${self.tweetPromote()}
                ${self.tweetPromoteOpened()}
                ${self.tweetPromote()}
              </div>
            </%doc>
          </div>
          <div class="pledgedPromoteWrapper">
            <%doc>
              ${pledgedPromote()}
              <div class="tweetPromoteWrapper">
              </div>
            </%doc>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
