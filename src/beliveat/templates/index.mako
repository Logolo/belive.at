<%inherit file="beliveat:templates/layout.mako" />

Hello ${world}.

<div class="container-fluid">
  <div class="row-fluid">
    <div id="assignmentColumn" class="span6">
      <h3>Assignments</h3>
      <div id="addAssignmentBlock">
        <div class="addAssignment"></div>
        <div class="addAssignmentDetails"></div>
      </div>  
      <div id="sortedAssignmentsBlock">
        <div class="assignment"></div>
        <div class="assignment"></div>
        <div class="assignment"></div>        
      </div>
    </div>
    <div id="coverageColumn" class="span6">
      <h3>Coverage</h3>
      <div id="pledgedCoverBlock">
      </div>
      <div id="pledgedPromoteBlock">
      </div>
    </div>
  </div>
</div>





// Assignments
<div class="assignment">
  <div class="promoteBlock">
    <span><img src="PATH_TO_PROMOTE_BUTTON" /></span>
    <span class="pledges">${PROMOTE_PLEDGES}</span>
    <span class="pledgesLabel">Pledges</span>
  </div>
  <div class="assignmentContent">
    <h3>${ASSIGNMENT_TITLE}</h3>
    <p>${ASSIGNMENT_BODY}</p>
    <span class="assignmentAuthor"><img src="${USERPIC}" />Submitted by ${USERNAME}.</span>
  </div>
  <div class="coverBlock">
    <span><img src="PATH_TO_COVER_BUTTON" /></span>
    <span class="pledges">${COVER_PLEDGES}</span>
    <span class="pledgesLabel">Pledges</span>
  </div>
</div>

// Tweets
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

// Pledges

// pledgeCoverBlock
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

// pledgePromoteBlock
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
