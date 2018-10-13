// Learn cc.Class:
//  - [Chinese] http://docs.cocos.com/creator/manual/zh/scripting/class.html
//  - [English] http://www.cocos2d-x.org/docs/creator/en/scripting/class.html
// Learn Attribute:
//  - [Chinese] http://docs.cocos.com/creator/manual/zh/scripting/reference/attributes.html
//  - [English] http://www.cocos2d-x.org/docs/creator/en/scripting/reference/attributes.html
// Learn life-cycle callbacks:
//  - [Chinese] http://docs.cocos.com/creator/manual/zh/scripting/life-cycle-callbacks.html
//  - [English] http://www.cocos2d-x.org/docs/creator/en/scripting/life-cycle-callbacks.html

import {bindChildren} from "../../core/cocosext"
import {wxext} from "../../wxext"

cc.Class({
    extends: cc.Component,

    properties: {
        // foo: {
        //     // ATTRIBUTES:
        //     default: null,        // The default value will be used only when the component attaching
        //                           // to a node for the first time
        //     type: cc.SpriteFrame, // optional, default is typeof default
        //     serializable: true,   // optional, default is true
        // },
        // bar: {
        //     get () {
        //         return this._bar;
        //     },
        //     set (value) {
        //         this._bar = value;
        //     }
        // },
    },

    // LIFE-CYCLE CALLBACKS:

    onLoad () {
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
           },
           {
               name: "richtext",
               type: cc.RichText,
           },
       ]
       bindChildren(this, children);
       this.progLoading.progress = 0.0;
    },

    gotoMainGame : function() {
        // cc.director.loadScene("main", function() {
        //     console.log("main scene load completed");
        // });
        
    },

    login: function() {
        var self = this;
        self.progLoading.lblProgress.string = "waiting for wechat login...";
        wxext.login(function(res) {
            var strResult = JSON.stringify(res);
            self.richtext.string = strResult;
            self.progLoading.lblProgress.string = "login successfully, waiting for server\'s process";
        });
    },

    start () {
        var progLoading = this.progLoading;
        var self = this;
        //initialize input events
        var listener =  cc.EventListener.create({
            event: cc.EventListener.TOUCH_ONE_BY_ONE,
            swallowTouches: true,
            onTouchBegan: function(touch, event) {
                var target = event.getCurrentTarget();

                var pos = touch.getLocation();

                if (progLoading.progress >= 1) {
                    self.gotoMainGame();
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

        var prog = this.progLoading.progress;
        prog += 0.01;
        prog = prog > 1 ? 1 : prog;

        this.progLoading.progress = prog;

        if (prog < 1) {
            var percent = cc.js.formatStr("loading %s%%", Math.floor(prog * 100));
            this.progLoading.lblProgress.string = percent;
        }

        if (prog >= 1 && !this.lblTouchBegin.node.active) {
            this.lblTouchBegin.node.active = true;

            var fadeAction = cc.scaleTo(1.5, 1.5, 1.5);
            var fadeAction2 = cc.scaleTo(1.0, 1.0, 1.0);
            var callbackFunc = cc.callFunc(function(node) {
                var seq = cc.sequence(fadeAction, fadeAction2, callbackFunc);
                node.runAction(seq);
            })
            var seq = cc.sequence(fadeAction, fadeAction2, callbackFunc);
            this.lblTouchBegin.node.runAction(seq);

            this.login();
        }
    },
});
