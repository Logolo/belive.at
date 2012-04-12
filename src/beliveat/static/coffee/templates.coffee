# Templates.
define 'beliveat.templates', (exports) ->
    
    assignment = mobone.string.template """
            
            <li>Assignment</li>
            
            
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

