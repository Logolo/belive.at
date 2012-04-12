<%inherit file="beliveat:templates/layout.mako" />

<%def name="sub_title()">
  ${_(u'Dashboard')}
</%def>

<div id="dashboard-view">
  <h1>#Syria</h1>
  <div class="container-fluid">
    <div class="row-fluid">
      <div id="assignmentColumn" class="span6">
        <h3>Assignments</h3>
        <div id="addAssignmentBlock">
          <form class="navbar-search pull-left" action="">
            <div id="addAssignment">
              <input type="text" placeholder="+ Add a new assignment">
            </div>
            <div id="addAssignmentDetails">
              <input type="textarea"></input>
              <button></button>
            </div>
          </form>
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



