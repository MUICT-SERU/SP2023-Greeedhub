from  lib import redisMessage

r = redisMessage()

if __name__ == '__main__':
    for a in range(1,100):
        e = "id:"+str(a)
        r.addGroup("test",e)
        r.sendGroup("test",e)