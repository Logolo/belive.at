# Backbone view classes.
define 'beliveat.view', (exports) ->
    
    # Unpack namespace.
    dispatcher = beliveat.events.dispatcher
    
    ### Widgets.
    ###
    
    # Base class for widgets.
    class BaseWidget extends Backbone.View
        initialize: ->
            @model.bind 'change', @render
            @model.bind 'destroy', @remove
            @model.view = this
            @render()
        
    
    # View for a "normal" assignment listing that's available to promote or cover.
    class AssignmentWidget extends BaseWidget
        events:
            'click .coverBlock':    'handle_cover'
            'click .promoteBlock':  'handle_promote'
        
        handle_cover: =>
            @create_offer 'cover', beliveat.model.cover_offers
            false
        
        handle_promote: =>
            @create_offer 'promote', beliveat.model.promote_offers
            false
        
        create_offer: (offer_type, target_collection) ->
            story = @model.get 'story'
            id = @model.get 'id'
            # Post to the server to create the offer.
            stub = "/stories/#{story}/assignments/#{id}"
            url = "#{stub}/#{offer_type}_offers/@@create"
            $.ajax
                url: url
                dataType: "json"
                type: "POST"
                # If the request was successful, add the cover offer to the
                # cover offers collection and remove this model.
                success: (data) =>
                    target_collection.add data
                    switch offer_type
                        when 'cover' then key = 'covering'
                        when 'promote' then key = 'promoting'
                    data = {}
                    data[key] = true
                    @model.set data
        
        render: => 
            @$el.html beliveat.templates.assignment @model.toJSON()
        
    
    # View for an assignment that's been selected to cover.
    class CoverOfferWidget extends BaseWidget
        events:
            'click .pledgedCoverClose': 'handle_close'
        
        handle_close: =>
            story = @model.get 'story'
            assignment = @model.get 'assignment'
            id = @model.get 'id'
            # Post to the server to close the assignment.
            stub = "/stories/#{story}/assignments/#{assignment}"
            url = "#{stub}/cover_offers/#{id}/@@close"
            $.ajax
                url: url
                dataType: "json"
                type: "POST"
                success: (data) => @model.collection.remove @model
            false
        
        render: => @$el.html beliveat.templates.cover_offer @model.toJSON()
    
    # View for a tweet that's a candidate to cover an assignment with.
    class CoverTweetWidget extends BaseWidget
        states:
            linked: 'LINKED'
            hidden: 'HIDDEN'
        events: 
            'click .buttonHide':                  'hide'
            'click .buttonLink .dropdown-menu a': 'link'
        
        hide: =>
            $.ajax
                url: "/tweets/#{@model.get('id_str')}/@@hide"
                dataType: "json"
                type: "POST"
                success: => @model.set state: @states.hidden
            false
        
        link: (event) =>
            # Get the target offer from the link clicked.
            $target = $ event.target
            $anchor = $target.closest 'a'
            offer_id = $anchor.attr 'data-offer'
            offer = beliveat.model.cover_offers.get offer_id
            # Construct the url.
            assignment = offer.get 'assignment'
            story = offer.get 'story'
            stub = "/stories/#{story}/assignments/#{assignment}"
            url = "#{stub}/cover_offers/#{offer_id}/@@link"
            # Construct the POST data.
            data =
                tweet_id: @model.get 'id_str'
            $.ajax
                url: url
                data: data
                dataType: "json"
                type: "POST"
                success: (data) =>
                    @model.set coverage_record: data, state: @states.linked
            false
        
        render: => 
            if not @collection.length
                @$el.hide()
            else
                @$el.show()
            state = @model.get 'state'
            console.log 'CoverTweetWidget.render', state
            if state is @states.hidden
                beliveat.model.own_tweets.remove @model
            else 
                @$el.html beliveat.templates.cover_tweet @model.toJSON()
        
        initialize: ->
            # Re-render when the cover offer collection changes.
            @collection = beliveat.model.cover_offers
            @collection.bind 'add remove reset', @render
            # Start unlinked.
            @model.set state: @states.unlinked 
            # Init.
            super()
        
    
    # View for an assignment that's been selected to promote.
    class PromoteOfferWidget extends BaseWidget
        events:
            'click .buttonPromoteClose': 'handle_close'
        handle_close: =>
            story = @model.get 'story'
            assignment = @model.get 'assignment'
            id = @model.get 'id'
            # Post to the server to close the assignment.
            stub = "/stories/#{story}/assignments/#{assignment}"
            url = "#{stub}/promote_offers/#{id}/@@close"
            $.ajax
                url: url
                dataType: "json"
                type: "POST"
                success: (data) =>
                    # Remove the offer.
                    @model.collection.remove @model
                    # XXX remove the tweets
            false
        
        render: => 
            @$el.html beliveat.templates.promote_offer @model.toJSON()
        
        initialize: =>
            # Init.
            super()
            # Setup a collection of tweets to promote.
            @collection = new beliveat.model.TweetCollection @model.get 'tweets'
            $tweets_wrapper = @$ '.tweetPromoteWrapper'
            @tweets_listing = new PromoteTweetsListing
                collection: @collection
                el: $tweets_wrapper
            # Add tweets broadcast to this promote offer.
            key = "tweet_to_promote_offer:#{@model.id}"
            dispatcher.on key, (data) => @collection.add data
        
    
    # View for a tweet that's a candidate to promote.
    class PromoteTweetWidget extends BaseWidget
        events: 
            'click .buttonHide'     : 'hide'
            'click .buttonRetweet'  : 'retweet'
            'click .buttonFlag'     : 'flag'
        
        flag: => @fulfill 1
        hide: => @fulfill 3
        retweet: => @fulfill 5
        fulfill: (code) =>
            # Get the target offer.
            $target = @$el.closest '.promote-offer'
            offer_id = $target.attr 'data-id'
            offer = beliveat.model.promote_offers.get offer_id
            # Build the url
            assignment = offer.get 'assignment'
            story = offer.get 'story'
            stub = "/stories/#{story}/assignments/#{assignment}"
            url = "#{stub}/promote_offers/#{offer_id}/@@fulfill"
            # Build the POST data.
            data = 
                tweet_id: @model.get 'id_str'
                action_code: code
            # Ping the server.
            $.ajax
                url: url
                data: data
                dataType: "json"
                type: "POST"
                success: (data) => @model.set data
            false
        
        render: =>
            @$el.html beliveat.templates.promote_tweet @model.toJSON()
        
    
    # View for the create assignment UI.
    class CreateAssignmentWidget extends Backbone.View
        states:
            'close':        'CLOSE'
            'error':        'ERROR'
            'open':         'OPEN'
            'reset':        'RESET'
            'success':      'SUCCESS'
        events:
            'click .close': 'handle_close'
            'focus form':   'handle_focus'
            'submit form':  'handle_submit'
        
        handle_close: => 
            @model.set state: @states.close
            false
        
        handle_focus: =>
            @model.set state: @states.open
        
        handle_submit: =>
            # Get the form data.
            $form = @$ 'form'
            data = {}
            data[item.name] = item.value for item in $form.serializeArray()
            # POST to the server to subscribe.
            $.ajax
                url: $form.attr 'action'
                data: data
                dataType: "json"
                type: "POST"
                success: (data) =>
                    beliveat.model.your_assignments.add data
                    @model.set state: @states.success
                error: (transport) =>
                    data = state: @states.error
                    if transport.status is 400
                        data['errors'] = JSON.parse transport.responseText
                    @model.set data
            # Show the progress indicator.
            @model.set state: @states.progress
            # Squish the original submit event.
            false
        
        render: => 
            state = @model.get 'state'
            # XXX clear any error / success classes.
            switch state
                when @states.close
                    $target = @$ '#addAssignmentDetails'
                    $target.slideUp()
                when @states.error
                    console.log 'error'
                    errors = @model.get 'errors'
                    console.log errors
                    # XXX set error on each control group
                when @states.open
                    $target = @$ '#addAssignmentDetails'
                    $target.slideDown()
                when @states.reset
                    $target = @$ 'form'
                    $target[0].reset()
                    @model.set state: @states.close
                when @states.success
                    @model.set state: @states.reset
        
        initialize: ->
            # Start closed and render when anything changes.
            $target = @$ '#addAssignmentDetails'
            $target.hide()
            @model.set state: @states.close
            @model.bind 'change', @render
            @render()
        
    
    
    ### Listings.
    ###
    
    # Base class for listings.
    class BaseListing extends Backbone.View
        initialize: ->
            @collection.bind 'add', @add
            @collection.bind 'reset', => @collection.each @add
            @collection.bind 'remove', (instance) => instance.view.remove()
            @collection.each @add
        
    
    # View for the assignments listing.
    class YourAssignmentsListing extends BaseListing
        add: (instance) =>
            widget = new AssignmentWidget model: instance
            @$el.prepend widget.$el
        
    
    # View for the assignments listing.
    class PopularAssignmentsListing extends BaseListing
        add: (instance) =>
            if instance.get('author') isnt beliveat.user
                widget = new AssignmentWidget model: instance
                @$el.prepend widget.$el
        
    
    # View for the listing of cover offers.
    class CoverOffersListing extends BaseListing
        add: (instance) =>
            widget = new CoverOfferWidget model: instance
            @$el.prepend widget.$el
        
    
    # View for the listing of cover offers.
    class CoverageTweetsListing extends BaseListing
        add: (instance) =>
            widget = new CoverTweetWidget model: instance
            @$el.prepend widget.$el
        
    
    # View for the listing of cover offers.
    class PromoteTweetsListing extends BaseListing
        add: (instance) =>
            widget = new PromoteTweetWidget model: instance
            @$el.prepend widget.$el
        
    
    # View for the listing of promote offers.
    class PromoteOffersListing extends BaseListing
        add: (instance) =>
            widget = new PromoteOfferWidget model: instance
            @$el.prepend widget.$el
        
    
    
    ### Pages.
    ###
    
    # View for the Story Page.
    class StoryView extends Backbone.View
        
        # Handle the arrival of a tweet that's a candidate to be used to cover
        # an assignment.
        handle_own_tweet: (data) -> beliveat.model.own_tweets.add(data)
        
        # Handle the arrival of a tweet that's been verified by its author as
        # coverage of an assignment this user has offered to promote by
        # re-broadcasting to the relevant promote offer widget to pick up.
        handle_tweet_to_promote: (data) ->
            console.log 'StoryView.handle_tweet_to_promote'
            dispatcher.trigger "tweet_to_promote_offer:#{data.offer}", data.tweet
        
        initialize: ->
            @hashtag = beliveat.story
            # Create assignment widget, passing through the hashtag.
            $create_assignment_el = @$ "#addAssignmentBlock"
            @create_assignment_widget = new CreateAssignmentWidget
                el: $create_assignment_el
                model: new Backbone.Model
            # Assignments listings.
            $your_assignments_el = @$ "#yourAssignmentsBlock ul"
            $popular_assignments_el = @$ "#sortedAssignmentsBlock ul"
            @your_assignments_listing = new YourAssignmentsListing
                collection: beliveat.model.your_assignments
                el: $your_assignments_el
            @popular_assignments_listing = new PopularAssignmentsListing
                collection: beliveat.model.popular_assignments
                el: $popular_assignments_el
            # Cover offers and own tweets listings.
            $cover_offers_el = @$ ".pledgedCoverBlock .pledgedCoverWrapper"
            $own_tweets_el = @$ ".pledgedCoverBlock .tweetCoverWrapper"
            @cover_offers_listing = new CoverOffersListing
                collection: beliveat.model.cover_offers
                el: $cover_offers_el
            @own_tweets_listing = new CoverageTweetsListing
                collection: beliveat.model.own_tweets
                el: $own_tweets_el
            # Promote offers listing.
            $promote_offers_el = @$ ".pledgedPromoteBlock"
            @promote_offers_listing = new PromoteOffersListing
                collection: beliveat.model.promote_offers
                el: $promote_offers_el
            # Bind to socket notifications.
            dispatcher.on "own_tweet:#{@hashtag}", @handle_own_tweet
            dispatcher.on "tweet_to_promote:#{@hashtag}", @handle_tweet_to_promote
        
    
    exports.StoryView = StoryView
