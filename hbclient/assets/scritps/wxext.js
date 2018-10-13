var wxext = {
    // compareVersion: function (v1, v2) {
    //     v1 = v1.split('.');
    //     v2 = v2.split('.');
    //     var len = Math.max(v1.length, v2.length);
    //     while (v1.length < len) {
    //         v1.push('0');
    //     }
    //     while (v2.length < len) {
    //         v2.push('0');
    //     }
    //     for (var i = 0; i < len; i++) {
    //         var num1 = parseInt(v1[i]);
    //         var num2 = parseInt(v2[i]);
    //         if (num1 > num2) {
    //             return 1;
    //         } else if (num1 < num2) {
    //             return -1;
    //         }
    //     }
    //     return 0;
    // },

    isWechatPlat: function() {
        return cc.sys.platform === cc.sys.WECHAT_GAME;
    },

    // isCanShowVideo: function(){
    //     if (!this.isWechatPlat()) {
    //         return false;
    //     }
    //     var current_version = wx.getSystemInfoSync().SDKVersion;
    //     if (this.compareVersion(current_version, "2.0.4") === -1){
    //         console.log('=====版本不够2.0.4，视频广告不能用')
    //         return false;
    //     }
    //     return true;
    // },

    // createVideo: function(self){ //创建视频
    //     if(!this.isCanShowVideo()) {
    //         return;
    //     }
    //     if(!this.videoAd){
    //         this.videoAd = wx.createRewardedVideoAd({adUnitId: 'adunit-e0dd75038579c0c7'});
    //     }
    //     this.videoAd.bind_this = self;
    //     this.videoAd.onClose(this.videoAd.bind_this.adSuccessPlay);
    // },

    // releaseVideo: function(){ //释放视频
    //     if(!this.isCanShowVideo()) {
    //         return;
    //     }
    //     if(this.videoAd && this.videoAd.bind_this){
    //         this.videoAd.offClose(this.videoAd.bind_this.adSuccessPlay);
    //         this.videoAd.bind_this = null;
    //     }
    // },

    // loadVideo: function(){ //加载并播放视频
    //     if(!this.isCanShowVideo()) {
    //         return;
    //     }
    //     if(this.isSoundOn == 1 && this.bgmId){
    //         cc.audioEngine.pause(this.bgmId); //停止背景音乐
    //     }
    //     this.videoAd.load().then(() => this.videoAd.show().catch(err => console.log(err)));
    // },
    
    login: function(callback) {
        if (!this.isWechatPlat()) {
            console.log('this is not wechat platform');
            callback({
                code : -1,
                msg : "it's not wechat",
            });
            return;
        }
        wx.login({
            success: function (res) {
                console.log(res);
                // res.code 为用户的登录凭证
                if (res.code) {
                  // 游戏服务器处理用户登录
                }
                else {
                  // 失败处理
                  console.log('获取用户登录态失败！' + res.errMsg);
                }
                callback(res);
            },
            fail: function (res) {
                // 失败处理
                console.log('用户登录失败！' + res.errMsg);
                callback(res);
            }
        });
    },

    // shareAppSingle: function(){ //分享按钮
    //     if (!this.isWechatPlat()) {
    //         console.log("it's not wechat platform");
    //         return;
    //     }
    //     cc.log("点击分享按钮");
    //     this.playBtnSound();
    //     //主动拉起分享接口
    //     cc.loader.loadRes("texture/share",function(err,data){
    //         wx.shareAppMessage({
    //             title: "不怕，就来PK！",
    //             imageUrl: data.url,
    //             success(res){
    //                 console.log("转发成功!!!");
    //             },
    //             fail(res){
    //                 console.log("转发失败!!!");
    //             },
    //         })
    //     });
    // },

    // enableGroupShare: function(enabled) {
    //     if (!this.isWechatPlat()) {
    //         console.log("it's not wechat platform");
    //         return;
    //     }
    //     //微信开启群分享
    //     wx.updateShareMenu({
    //         withShareTicket: enabled
    //     });
    // },
    
    // shareToGroup: function() {
    //     if (!this.isWechatPlat()) {
    //         console.log("it's not wechat platform");
    //         return;
    //     }
    //     cc.loader.loadRes("texture/share",function(err,data){
    //         wx.shareAppMessage({
    //             title: "经典小游戏始终好玩如初，来吧！一起来回味吧！",
    //             imageUrl: data.url,
    //             success(res){
    //                 console.log("转发成功!!!");
    //                 if(res.shareTickets == null || res.shareTickets == undefined || res.shareTickets == ""){ //没有群信息，说明分享的是个人
    //                     console.log("res.shareTickets is null");
    //                     self.showTipsUI("请分享到群获得生命值");
    //                 }
    //                 else{ //有群信息
    //                     console.log("res.shareTickets is not null");
    //                     if(res.shareTickets.length > 0) { 
    //                         //TODO
    //                     }
    //                 }
    //             },
    //             fail(res){
    //                 console.log("转发失败!!!");
    //             } 
    //         });
    //     });
    // },
}

export {wxext};