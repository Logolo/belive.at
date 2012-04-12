<%inherit file="beliveat:templates/layout.mako" />

<%def name="sub_title()">
  ${_(u'Dashboard')}
</%def>

<%def name="assignment()">
  <div class="assignment">
    <div class="promoteBlock">
      <span><img src="PATH_TO_PROMOTE_BUTTON" /></span>
      <span class="pledges">42</span>
      <span class="pledgesLabel">Pledges</span>
    </div>
    <div class="assignmentContent">
      <h3>Cover police behaviour at Occupy London next Friday.</h3>
      <p>A bunch of students will be congregating outside St. Paul's cathedral to show support. We want to make sure that there is peace and order...</p>
      <span class="assignmentAuthor"><img src="" />Submitted by TheOccupyGuy.</span>
    </div>
    <div class="coverBlock">
      <span><img src="PATH_TO_COVER_BUTTON" /></span>
      <span class="pledges">23</span>
      <span class="pledgesLabel">Pledges</span>
    </div>
  </div>
</%def>

<%def name="tweetCover()">
  <div class="tweetCover">
    <div class="tweetText">
      <h3>"TWEET_TITLE"</h3>
      <p>TWEET_BODY</p>
      <div class="tweetButtons">
        <div class="btn-group buttonLink">
          <a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
            Link to Assignment
            <span class="caret"></span>
          </a>
          <ul class="dropdown-menu">
            <!-- dropdown menu links - iterate through COVER_PLEDGES -->
            <li><a href="#">Cover Pledge #1</li>
            <li><a href="#">Cover Pledge #2</li>
            <li><a href="#">Cover Pledge #3</li>
          </ul>
        </div>
        <button class="buttonHide">Hide</button>
      </div>
    </div>
    <iframe class="youtube-player" type="text/html" width="640" height="385" src="http://www.youtube.com/embed/${VIDEO_ID}" frameborder="0">
    </iframe>
  </div>
</%def>

<%def name="tweetPledge()">
  <div class="tweetPledge">
    <iframe class="youtube-player" type="text/html" src="http://www.youtube.com/embed/${VIDEO_ID}" frameborder="0"> <!-- default sizes = width="640" height="385" -->
    </iframe>
    <div class="tweetText">
      <h3>${TWEET_TITLE}</h3><img src="${TWEET_AUTHOR_PIC}" />
      <p>${TWEET_BODY}</p>
      <div class="tweetButtons">
        <button class="buttonFlag"><img src="PATH_TO_FLAG_IMAGE" />Flag as Inappropriate</button>
        <button class="buttonRetweet">Retweet</button>
        <button class="buttonHide">Hide</button>
      </div>
    </div>
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
                  <a class="btn" href="#close">Close</a>
                </div>
              </div>
            </fieldset>
          </form>
        </div>  
        <div id="sortedAssignmentsBlock">
          ${self.assignment()}
          ${self.assignment()}
          ${self.assignment()}  
        </div>
      </div>
      <div id="coverageColumn" class="span6">
        <h3>Coverage</h3>
        <div class="pledgedCoverBlock">
          <div class="pledgedCoverWrapper">
            <div class="pledgedCover"></div>
            <div class="pledgedCover"></div>
          </div>
          <div class="tweetCoverWrapper">
            <div class="tweetCover"></div>
            <div class="tweetCover"></div>
          </div>
        </div>
        <div class="pledgedPromoteBlock">
          <div class="pledgedPromoteWrapper">
            <div class="pledgedPromote"></div>
            <div class="tweetPromoteWrapper">
              <div class="tweetPromote"></div>
              <div class="tweetPromote"></div>
              <div class="tweetPromote"></div>
            </div>
          </div>
          <div class="pledgedPromoteWrapper">
            <div class="pledgedPromote"></div>
            <div class="tweetPromoteWrapper">
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
