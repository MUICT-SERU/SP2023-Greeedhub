import redis

pool = redis.ConnectionPool(host='127.0.0.1', port=6379)
r = redis.Redis(connection_pool=pool,db=0)

class redisMessage():
    def __init__(self):
        self.r = r
        file = open("./groupsend.lua")
        script = file.read()
        self.hash = self.r.script_load(script)

    def addGroup(self,group,name):
        self.r.sadd(group,name)


    def sendGroup(self,group,msg):
        args = (group, msg)
        resout = r.evalsha(self.hash, 1, *args)
        return  resout