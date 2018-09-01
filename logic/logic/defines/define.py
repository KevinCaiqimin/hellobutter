class Define:
    
    @staticmethod
    def getCacheKeyUser(uid):
        return format("user_%d" % uid)
    
    @staticmethod
    def getCacheKeyChannelUser(channelId, channelUid):
        return format("channeluser_%s_%s" % (channelId, channelUid))