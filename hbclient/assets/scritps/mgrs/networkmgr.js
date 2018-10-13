
function Message(cmd, data) {
    this.cmd = cmd;
    this.data = data;
    this.resp = "";
}

function NetworkMgr(svrAddr) {
    this.svrAddr = svrAddr
    this.msgs = new Array();
}

NetworkMgr.prototype = {
    construstor: NetworkMgr,
    send : function(cmd, data, caller, callback) {
        var xhr = new XMLHttpRequest()
        xhr.onreadystatechange = function() {
            if (xhr.readyState == 4 && xhr.status >= 200 && xhr.status <= 400) {
                var resp = xhr.responseText
                var obj = JSON.parse(resp);
                if (callback != undefined) {
                    callback.call(caller, obj);
                }
                else {
                    console.log("there is no corresponding process function of " + cmd);
                }
            }
        }
        xhr.open("POST", this.svrAddr);

        var dataStr = JSON.stringify(data);
        xhr.send(dataStr);
    }
}

