import redis


class redisMessage():
    def __init__(self,host='127.0.0.1', port=6379,db=0):
        self.pool = redis.ConnectionPool(host,port)
        self.conn = redis.Redis(connection_pool=pool,db)
        self.script ="""
        local status = true
        local groupname = KEYS[1]
        local msg = ARGV[1]
        local grouplist = redis.call("SMEMBERS",groupname)
        for item  in ipairs(grouplist) do
        status = redis.call("lpush",item,msg)
        end
        return status
        """
        self.hash = self.conn.script_load(self.script)

    def addGroup(self,group,name):
        self.conn.sadd(group,name)

    def removeGroup(self,group,name):
        self.conn.srem(group,name)

    def sendGroup(self,group,msg):
        args = (group, msg)
        resout = self.conn.evalsha(self.hash, 1, *args)
        return  resout