class Define:
    
    @staticmethod
    def getCacheKeyChannelUser(channelId, channelUid):
        return format("channeluser_%s_%s" % (channelId, channelUid))
    
    @staticmethod
    def getLockKeyChannelUser(channelId, channelUid):
        return format("lock_channeluser_%s_%s" % (channelId, channelUid))
    
    @staticmethod
    def getCacheKeyUid():
        return format("autoascuid")