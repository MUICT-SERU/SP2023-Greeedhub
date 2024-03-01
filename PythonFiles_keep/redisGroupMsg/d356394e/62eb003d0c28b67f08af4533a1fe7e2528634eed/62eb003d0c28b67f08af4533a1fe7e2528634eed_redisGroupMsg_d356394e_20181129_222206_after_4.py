from redisGroupMsg import redisMessage
r = redisMessage()

if __name__ == '__main__':
    conn = r.conn
    msg = conn.rpop("id:1")
    print(msg)