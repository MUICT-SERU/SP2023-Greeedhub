from  lib import redisMessage
import datetime
r = redisMessage()

if __name__ == '__main__':
    starttime = datetime.datetime.now()

    # for a in range(1,1000):
    #     e = "id:"+str(a)
    #     # r.addGroup("test",e)
    #     r.sendGroup("test",e)
    b = r.r.smembers("test")
    for c in b:
        # print(c)
        for a in range(1,1000):
            r.r.lpush(c,"hello world")
    endtime = datetime.datetime.now()
    print( (endtime - starttime))
