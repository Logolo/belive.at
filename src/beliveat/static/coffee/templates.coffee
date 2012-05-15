# Templates.
define 'beliveat.templates', (exports) ->
    
    assignment = mobone.string.template """
              <% if (!covering && !promoting) { %>
                <li class="assignment" data-id="<%- id %>">
                  <% if (covering) { %>
                    <div class="coverBlock noclick">
                  <%} else {%>
                    <div class="coverBlock">
                  <% } %>                
                    <% if (!covering) { %>
                      <a href="#cover">
                    <% } %>
                        <div>
                          <img src="<%- assetgen.static_path('/static/gfx/cover.png') %>" />
                        </div>
                        <div class="pledges">
                          <%= num_coverage_offers %>
                        </div>
                        <div class="pledgesLabel">
                          Reporters
                        </div>
                    <% if (!covering) { %>
                      </a>
                    <% } %>
                  </div>

                  <% if (promoting) { %>
                    <div class="promoteBlock noclick">
                  <%} else {%>
                    <div class="promoteBlock">
                  <% } %> 

                    <% if (!promoting) { %>
                      <a href="#support">
                    <% } %>
                        <div>
                          <img src="<%- assetgen.static_path('/static/gfx/promote.png') %>" />
                        </div>
                        <div class="pledges">
                          <%= num_promotion_offers %>
                        </div>
                        <div class="pledgesLabel">
                          Amplifiers
                        </div>
                    <% if (!promoting) { %>                      
                      </a>
                    <% } %>
                  </div>
                  <div class="assignmentContent">
                    <h3><%= title %></h3>
                    <p><%~ description %></p>
                    <div class="assignmentAuthor">
                      <img src="<%- profile_image_url %>" />
                      Suggested by <%~ '@' + author %>.
                    </div>
                  </div>
                  <div class="clear"></div>
                </li>
              <% } %>
        """
    

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
    
    cover_tweet = mobone.string.template """         
            <li class="tweetCover">
              <div class="tweetText">
                <p><%= text %></p>
                <div class="tweetButtons">
                  <button class="buttonHide btn close">Hide</button>
                  <div class="btn-group buttonLink">
                    <a class="btn dropdown-toggle btn-primary" data-toggle="dropdown" href="#">
                      Link to Assignment
                      <span class="caret"></span>
                    </a>
                    <ul class="dropdown-menu">
                      <% beliveat.model.cover_offers.each(function (offer) { %>
                        <li>
                          <a href="#" data-id="<%- offer.get('title') %>">
                            <%= offer.get('title') %></a>
                        </li>
                      <% }); %>
                    </ul>
                  </div>
                </div>
              </div>
              <div class="clear"></div>
            </li>
        """

    cover_tweet_opened = mobone.string.template """
            
            <li>Cover Tweet</li>
            
            
        """

    promote_offer = mobone.string.template """
            <li class="pledgedPromote">
              <div class="pledgedPromoteBody">
                <div class="pledgedPromoteIcon"><img src="<%- assetgen.static_path('/static/gfx/promote-icon.png') %>" /></div>
                <div class="pledgedPromoteTitle"><%= title %></div>
                <div class="pledgedPromoteClose">
                   <button class="btn-mini buttonPromoteClose">x</button>
                </div>
              </div>
              <div class="clear"></div>
              <div class="pledgedPromoteStatus">You pledged to amplify this.</div>
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

