from redisGroupMsg import redisMessage
r = redisMessage()

if __name__ == '__main__':
    for a in range(1,10):
        e = "id:"+str(a)
        # r.addGroup("test",e)
        # r.sendGroup("test",e)
        r.removeGroup("test",e)

