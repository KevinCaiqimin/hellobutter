#!/bin/bash
#pid=`cat /tmp/match_service.pid`
#echo 'will kill pid', $pid
#kill -9 $pid
#sleep 3
#nohup python match_service.py & 
#npid=`cat /tmp/match_service.pid`
#ps -ef | grep $npid

pidfile=/tmp/match_service.pid
app=match_service

function check_pid() {
    if [ -f $pidfile ];then
        pid=`cat $pidfile`
        if [ -n $pid ]; then
            running=`ps -p $pid|grep -v "PID TTY" |wc -l`
            return $running
        fi
    fi
    return 0
}

function start() {
    check_pid
    running=$?
    if [ $running -gt 0 ];then
        echo -n "$app now is running already, pid="
        cat $pidfile
        return 1
    fi

    if ! [ -f $conf ];then
        echo "no config!"
        return 1
    fi
	nohup python match_service.py & 
    echo 'starting..'
    sleep 10
    status
}

function stop() {
    pid=`cat $pidfile`
    kill $pid
    rm -f $pidfile
    echo "$app stoped..."
}

function restart() {
    stop
    sleep 10
    start
}

function status() {
    check_pid
    running=$?
    if [ $running -gt 0 ];then
        echo started
        return 0
    else
        echo stoped
        return 1
    fi
}


function help() {
    echo "$0 start|stop|restart|status"
}

if [ "$1" == "" ]; then
    help
elif [ "$1" == "stop" ];then
    stop
elif [ "$1" == "start" ];then
    start
elif [ "$1" == "restart" ];then
    restart
elif [ "$1" == "status" ];then
    status
else
    help
fi
