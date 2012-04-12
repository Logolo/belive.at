<%inherit file="beliveat:templates/layout.mako" />

<%def name="sub_title()">
  ${_(u'Dashboard')}
</%def>

<%def name="assignment()">
  <li class="assignment">
    <div class="promoteBlock">
      <span><img src="/static/gfx/promote.png" /></span>
      <span class="pledges">42</span>
      <span class="pledgesLabel">Pledges</span>
    </div>
    <div class="assignmentContent">
      <h3>Cover police behaviour at Occupy London next Friday.</h3>
      <p>A bunch of students will be congregating outside St. Paul's cathedral to show support. We want to make sure that there is peace and order...</p>
      <span class="assignmentAuthor"><img src="/static/gfx/defaultUser.png" />Submitted by TheOccupyGuy.</span>
    </div>
    <div class="coverBlock">
      <span><img src="/static/gfx/cover.png" /></span>
      <span class="pledges">23</span>
      <span class="pledgesLabel">Pledges</span>
    </div>
  </li>
</%def>

<%def name="tweetCover()">
  <div class="tweetCover">
    <iframe class="youtube-player" type="text/html" src="http://www.youtube.com/embed/VIDEO_ID" frameborder="0">
    </iframe>
    <div class="tweetText">
      <h3>"YouTube video title here"</h3>
      <p>Tweet from the person promoting the video is here. Blah blah blah blah. Blah!</p>
      <div class="tweetButtons">
        <div class="btn-group buttonLink">
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
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
  </div>
</%def>

<%def name="tweetPromote()">
  <div class="tweetPromote">
    <iframe class="youtube-player" type="text/html" src="http://www.youtube.com/embed/VIDEO_ID" frameborder="0"> <!-- default sizes = width="640" height="385" -->
    </iframe>
    <div class="tweetText">
      <h3>"YouTube video title here"</h3><img src="/static/gfx/defaultUser.png" />
      <p>Tweet from the person promoting the video is here. Blah blah blah blah. Blah!</p>
      <div class="tweetButtons">
        <button class="buttonFlag"><img src="/static/gfx/flag.png" />Flag as Inappropriate</button>
        <button class="buttonRetweet">Retweet</button>
        <button class="buttonHide">Hide</button>
      </div>
    </div>
  </div>
</%def>

<%def name="pledgedCover()">
  <div class="pledgedCover">
    <div class="pledgedCoverBody">
      <div class="pledgedCoverTitle">"Film the awesome blah, blah blah."</div>
      <div class="pledgedCoverIcon">
        <img src="/static/gfx/cover-icon.png" />
        <i class="icon-remove-circle"></i>
      </div>
    </div>
    <div class="pledgedCoverStatus">You pledged to report on this.</div>
  </div>
</%def>

<%def name="pledgedPromote()">
  <div class="pledgedPromote">
    <div class="pledgedPromoteBody">
      <div class="pledgedPromoteIcon"><img src="/static/gfx/promote-icon.png" /></div>
      <div class="pledgedPromoteTitle">"Get footage of nuclear waste train next to church."</div>
    </div>
    <div class="pledgedPromotestatus">You fulfilled your pledge to retweet reports on this.</div>
  </div>
</%def>


<div id="dashboard-view">
  <h1>#Syria</h1>
  <div class="container-fluid">
    <div class="row-fluid">
      <div id="assignmentColumn" class="span6">
        <h3>Assignments</h3>
        <div id="addAssignmentBlock">
          <form action="${request.route_url('assignments', traverse=('create',))}"
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
          <ul>
            ${self.assignment()}
          </ul>
        </div>
        <div id="sortedAssignmentsBlock">
          <h4>Popular Assignments</h4>
          <ul>
            ${self.assignment()}
            ${self.assignment()}  
          </ul>
        </div>
      </div>
      <div id="coverageColumn" class="span6">
        <h3>Coverage</h3>
        <div class="pledgedCoverBlock">
          <div class="pledgedCoverWrapper">
            <div class="pledgedCover">
              ${self.pledgedCover()}
            </div>
            <div class="pledgedCover">
              ${self.pledgedCover()}
            </div>
          </div>
          <div class="tweetCoverWrapper">
            ${self.tweetCover()}
            ${self.tweetCover()}
          </div>
        </div>
        <div class="pledgedPromoteBlock">
          <div class="pledgedPromoteWrapper">
            ${pledgedPromote()}
            <div class="tweetPromoteWrapper">
              ${self.tweetPromote()}
              ${self.tweetPromote()}
              ${self.tweetPromote()}
            </div>
          </div>
          <div class="pledgedPromoteWrapper">
            ${pledgedPromote()}
            <div class="tweetPromoteWrapper">
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
