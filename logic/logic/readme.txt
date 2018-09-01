0. 通用字段说明：
RTID(包括大写或者小写形式)：赛事ID（字符串）
ROLL: 轮（即每一场中第几轮）（整数）
ROOMID: 房间ID(长整数)

机器人UID后两位数：99

1. 玩家基本信息
存储RedisKey: user_UID, 如user_1911
存储值：json
结构：{
    uid = 0
    nation = 0, #玩家国旗
    nickName = "",
    headUrl = "",
    lv = 0,
}

2. 玩家阵容
存储RedisKey: userdefend_RTID_UID_ROLL, 如赛事1233，第3轮，玩家1911的阵容存储key: userdefend_1233_1911_3
存储值：json
结构：{
    uid = 0
    rtId = ""
    roll = -1
    defendChars = [
        {
            charId = "xxx",
            charLv = 0,
            evoLv = 0,
            charEvoLv = 0,
        },
        ...
    ],
}

3. 赛事配置信息
存储RedisKey: rtbattle_RTID
存储值：json
结构：{
    rtId = "undefine" #赛事ID
    battleId = 0
    battleType = 0 #赛事类型（1：常规赛，2：双周赛）
    startTime = 0 #赛事开始时间（秒级别时间戳）
    endTime = 0 #赛事结束时间（秒级别时间戳）
    curRoll = -1 #赛事进行到第几轮
    regions = 0 #赛事分多少个区
    version = "undefine"
    longId = 0
    rollReadyDuration = 0 #每一轮的玩家准备时间
    rollLastNSecondsEnterBattle = 0 #准备完成后倒数N秒进入战斗
    rollBattleDuration = 0 #每一轮的战斗时间
    rollWaitDuration = 0 #每一轮战斗结束后等待进入下一轮的时间
    signDeadlineTime = 0 #报名截止时间（时间戳）
    matchCheckTime = 0 #玩家报名后并匹配检查时间（理论上这个时间点，匹配服已经做好了第一轮匹配）（时间戳）
    signStartTime = 0 #报名开始时间（时间戳）
}

4. 房间信息
存储RedisKey: rtroom_ROOMID
存储值：json
结构：{
    roomId = 0
    rtId = ""
    regionId = "" #房间所在的区的ID
    rollNO = -1 #房间所属第几轮
    users = [] #房间里边的玩家ID（玩家UID在这个数组中的顺序代表了玩家的站位信息）
    innerRanks = {} #如果房间战斗结束，这里存放玩家在房间内的输赢排名信息，k,v结构，比如{"611":3, "1911":2, "35711":1}
}

5. 战斗服务器心跳
协议：rtServerHB
发送数据：json
{
    "ServerId" : "string",
    "ServerName" : "string",
    "ServerAddr" : "string",
}

6. 获取当前或者即将开始的赛事key
存储RedisKey: curavairt
获取值：RTId

7. 战斗胜利通知
协议：onRoomBattleEndNotify
发送数据：json
{
    "RTId" : "string",
    "RoomId" : 0,
    "Users" : [
        {
            "Uid": long,
            "AutoDoPercent": float,
            "InnerRank": int
        },
        ...
    ]
}
返回：json
{
    "code" : int(错误码，0：无错误）, 
    "msg" : "string"(错误消息)
}

8. 根据服务器ID获取相应房间
存储RedisKey: rtsvrid2room_SERVERID_RTID_ROLL
获取值：HASH
获取API: hgetall

9. 报名玩家信息
存储RedisKey: rtuser_UID
获取值：json
{
    uid = 0
    isNPC = False
    serverRegion = "undefine" #玩家所属大区名称，如us_east_1, cn_north_1
    subScore = 0
    addScore = 0
}

10. 房间战斗结果
存储RedisKey: btresult_ROOMID
存储值：json
{
    roomId = 0,
    users = [
        {
            uid = 0,
            autoDoPercent = 0.0f, #[0~1]
            innerRank = 0, #玩家在房间内的战斗排名（1,2,3）
        },
        ...
    ]
}