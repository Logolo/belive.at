# Templates.
define 'beliveat.templates', (exports) ->
    
    assignment = mobone.string.template """
            <li class="assignment">
              <div class="coverBlock">
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
              </div>
              <div class="promoteBlock">
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
        """
    
    cover_offer = mobone.string.template """
            
            <li>Cover Offer</li>
            
            
        """
    
    cover_tweet = mobone.string.template """
            
            <li>Cover Tweet</li>
            
            
        """
    
    promote_offer = mobone.string.template """
            
            <li>Promote Offer</li>
            
            
        """
    
    promote_tweet = mobone.string.template """
            
            <li>Promote Tweet</li>
            
            
        """
    
    exports.assignment = assignment
    exports.cover_offer = cover_offer
    exports.cover_tweet = cover_tweet
    exports.promote_offer = promote_offer
    exports.promote_tweet = promote_tweet

