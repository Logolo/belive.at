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
			<div class="columnTitle"></div>
			<div id="pledgedRetweetBlock">
			</div>
			<div id="pledgedCoverageBlock">
			</div>
		</div>
	</div>
</div>





// Assignments
<div class="assignment">
	<div class="promoteBlock">
		<span><img src="PATH_TO_PROMOTE_BUTTON" /></span>
		<span class="pledges">${PROMOTE_PLEDGES}</span>
		<span class="pledgesLabel">${_("Pledges")}</span>
	</div>
	<div class="assignmentContent">
		<h3>${ASSIGNMENT_TITLE}</h3>
		<p>${ASSIGNMENT_BODY}</p>
		<span class="assignmentAuthor"><img src="${USERPIC}" />${_("Submitted by")} ${USERNAME}.</span>
	</div>
	<div class="coverBlock">
		<span><img src="PATH_TO_COVER_BUTTON" /></span>
		<span class="pledges">${COVER_PLEDGES}</span>
		<span class="pledgesLabel">${_("Pledges")}</span>
	</div>
</div>

// Tweets
<div class="tweetCover">
	<div class="tweetText">
		<h3>${TWEET_TITLE}</h3>
		<p>${TWEET_BODY}</p>
		<div class="tweetButtons">
			<div class="btn-group">
				<a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
					Link to Assignment
					<span class="caret"></span>
				</a>
				<ul class="dropdown-menu">
					<li></li> <!-- dropdown menu links - iterate through COVER_PLEDGES -->
				</ul>
			</div>
			<button>${_("Hide")}</button>
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
			<button ><img src="PATH_TO_FLAG_IMAGE" />${_("Flag as Inappropriate")}</button>
			<div class="btn-group">
				<a class="btn dropdown-toggle" data-toggle="dropdown" href="#">
					Link to Assignment
					<span class="caret"></span>
				</a>
				<ul class="dropdown-menu">
					<li><a href="#">${PROMOTE_PLEDGES}</li> <!-- dropdown menu links - iterate through PROMOTE_PLEDGES -->
				</ul>
			</div>
			<button>${_("Hide")}</button>
		</div>
	</div>
</div>

// Pledges

pledgeCover


pledgePromote
