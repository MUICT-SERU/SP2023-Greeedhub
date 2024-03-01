#coding=utf8
import time
import storage, out, argparser, robot
from client import WeChatClient
from ChatLikeCMD import ChatLikeCMD

ROBOT = False

def demo_robot(s, msgList, client): # ONLY FOR DEMO
    print 'Start auto-replying'
    while True: 
        if msgList: 
            msg = msgList.pop()
            if s.find_nickname(msg['FromUserName']): robot.deal_with_msg(msg, s, client)
        time.sleep(.1)
if __name__ == '__main__':
    client_s = storage.Storage()
    if ROBOT:
        client = WeChatClient(client_s, robot = True)
    else:
        client = WeChatClient(client_s)

    client.login()
    msgList = client.storage()

    if ROBOT:
        demo_robot(client_s, msgList, client)
    else:
        front = ChatLikeCMD(header = str(client_s.find_nickname(client_s.userName)), symbol = '>', inPip = msgList)
        cmdList = front.get_command_pip()
        front.start()
        argparser.startCommandLine(client_s, client, msgList, front, cmdList)
