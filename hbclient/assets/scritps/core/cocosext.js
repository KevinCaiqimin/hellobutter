// var assert = require('assert');

function bindChildren(parentComp, childrenAry) {
    if (childrenAry == undefined) {
        console.log("specified children array is undefined");
        return;
    }
    if (parentComp == undefined) {
        console.log("parent is undefined");
        return;
    }
    var parent = parentComp.node;
    for (var i = 0; i < childrenAry.length; i++) {
        var child = childrenAry[i];
        var node = cc.find(child.name, parent);
        if (node == undefined) {
            console.log("child %s is undefined", child.name);
            continue;
        }
        var comp = node.getComponent(child.type);
        if (comp == undefined) {
            console.log("component of child %s is undefined", child.name);
            continue;
        }
        parentComp[child.name] = comp;

        if (child.children == undefined) {
            continue;
        }
        bindChildren(comp, child.children);
    }
}

export {bindChildren}