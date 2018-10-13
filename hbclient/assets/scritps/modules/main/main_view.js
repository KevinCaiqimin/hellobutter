
// import {bindChildren} from "../../core/cocosext";

cc.Class({
    extends: cc.Component,

    properties: {
    },

    // LIFE-CYCLE CALLBACKS:

    onLoad () {
        //specify children need to be exposed
         var children = [
            {
                name: "progLoading",
                type: cc.ProgressBar,
                children : [
                    {
                        name : "lblProgress",
                        type : cc.Label,
                    }
                ]
            },
            {
                name: "lblTouchBegin",
                type: cc.Label,
            }
        ]
        // bindChildren(this, children);
        this.progLoading.progress = 0.0;
    },

    gotoMainGame : function() {
        wx.getSystemInfo({
            success: function (res) {
              // res 一般是一个包含调用结果的对象
              console.log('This phone is ' + res.brand + ' ' + res.model);
            },
            fail: function (res) {
              // 通过 res.errMsg 可以获取错误信息
              console.warn(res.errMsg);
            },
            complete: function () {
              console.log('API call completed');
            }
          });
        // cc.director.loadScene("main", function() {
        //     console.log("main scene load completed");
        // });
    },

    start () {
        var progLoading = this.progLoading;
        var loading = this;
        //initialize input events
        var listener =  cc.EventListener.create({
            event: cc.EventListener.TOUCH_ONE_BY_ONE,
            swallowTouches: true,
            onTouchBegan: function(touch, event) {
                var target = event.getCurrentTarget();

                var pos = touch.getLocation();

                if (progLoading.progress >= 1) {
                    loading.gotoMainGame();
                }
                return true;
            },
            // onTouchMoved: function(touch, event) {
            //     var target = event.getCurrentTarget();
            //     var pos = touch.getLocation();
            //     console.log("touch moved");
            // },
            // onTouchEnded: function(touch, event) {
            //     var target = event.getCurrentTarget();
            //     var pos = touch.getLocation();
            //     console.log("touch ended");
            // },
            // onTouchCanceled: function(touch, event) {
            //     var target = event.getCurrentTarget();
            //     console.log("touch canceled");
            // }
        });
        cc.eventManager.addListener(listener, this.node);
    },
    


    update (dt) {
    },
    
});
