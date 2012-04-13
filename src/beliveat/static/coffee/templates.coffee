# Templates.
define 'beliveat.templates', (exports) ->
    
    assignment = mobone.string.template """
            <% if (!promoting || !covering) { %>
              <li class="assignment" data-id="<%- id %>">
                <div class="coverBlock">
                  <% if (!covering) { %>
                    <a href="#cover">
                      <div>
                        <img src="<%- assetgen.static_path('/static/gfx/cover.png') %>" />
                      </div>
                      <div class="pledges">
                        <%= num_coverage_offers %>
                      </div>
                      <div class="pledgesLabel">
                        Offers
                      </div>
                    </a>
                  <% } %>
                </div>
                <div class="promoteBlock">
                  <% if (!promoting) { %>
                    <a href="#support">
                      <div>
                        <img src="<%- assetgen.static_path('/static/gfx/promote.png') %>" />
                      </div>
                      <div class="pledges">
                        <%= num_promotion_offers %>
                      </div>
                      <div class="pledgesLabel">
                        Supporters
                      </div>
                    </a>
                  <% } %>
                </div>
                <div class="assignmentContent">
                  <h3><%= title %></h3>
                  <p><%~ description %></p>
                  <div class="assignmentAuthor">
                    <img src="<%- profile_image_url %>" />
                    Submitted by <%~ '@' + author %>.
                  </div>
                </div>
                <div class="clear"></div>
              </li>
            <% } %>
        """
    
    # variables: cover_offer_title
    cover_offer = mobone.string.template """
            <li class="pledgedCover" data-id="<%- id %>">
              <div class="pledgedCoverBody">
                <div class="pledgedCoverClose">
                   <button class="btn-mini buttonCoverClose">x</button>
                </div>
                <div class="pledgedCoverTitle"><%= title %></div>
                <div class="pledgedCoverIcon">
                  <img src="<%- assetgen.static_path('/static/gfx/cover-icon.png') %>" />
                </div>
              </div>
              <div class="clear"></div>
              <div class="pledgedCoverStatus">You pledged to cover this.</div>
            </li>
        """
    
    # required variables: youtube_video_id, youtube_video_title, tweet, cover_pledges[]
    #
    #
    cover_tweet = mobone.string.template """         
            <li class="tweetCover">
              <div class="tweetCoverLink">
                <a src="#YouTubeLink">
                  <img src="http://img.youtube.com/vi/<%= youtube_video_id %>/0.jpg" />
                </a>
              </div>
              <div class="tweetText">
                <h3></h3>
                <p><%= tweet %></p>
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
            </li>




            
            
        """

    cover_tweet_opened = mobone.string.template """
            
            <li>Cover Tweet</li>
            
            
        """

    # variables: promote_offer_title
    promote_offer = mobone.string.template """
            <li class="pledgedPromote">
              <div class="pledgedPromoteBody">
                <div class="pledgedPromoteIcon"><img src="<%- assetgen.static_path('/static/gfx/promote-icon.png') %>" /></div>
                <div class="pledgedPromoteTitle"><%= promote_offer_title %></div>
                <div class="pledgedPromoteClose">
                   <button class="btn-mini buttonPromoteClose">x</button>
                </div>
              </div>
              <div class="clear"></div>
              <div class="pledgedPromoteStatus">You pledged to promote this.</div>
            </li>            
        """
    
    promote_tweet = mobone.string.template """
            
            <li>Promote Tweet</li>
            
            
        """

    promote_tweet_opened = mobone.string.template """
            
            <li>Promote Tweet</li>
            
            
        """
    
    exports.assignment = assignment
    exports.cover_offer = cover_offer
    exports.cover_tweet = cover_tweet
    exports.cover_tweet_opened = cover_tweet_opened
    exports.promote_offer = promote_offer
    exports.promote_tweet = promote_tweet
    exports.promote_tweet_opened = promote_tweet_opened

