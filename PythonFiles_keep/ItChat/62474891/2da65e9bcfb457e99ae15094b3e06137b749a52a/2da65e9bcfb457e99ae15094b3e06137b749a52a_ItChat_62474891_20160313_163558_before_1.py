#coding=utf8
import time, sys
import itchat.storage, itchat.out, itchat.argparser, itchat.robot
from itchat.client import WeChatClient
from plugin.ChatLikeCMD import ChatLikeCMD

ROBOT = True

def demo_robot(s, msgList, client): # ONLY FOR DEMO
    print 'Start auto-replying'
    while True: 
        if msgList: 
            msg = msgList.pop()
            if s.find_nickname(msg['FromUserName']): itchat.robot.deal_with_msg(msg, s, client)
        time.sleep(.1)
if __name__ == '__main__':
    from PluginTest import plugin_load_succeed
    if not plugin_load_succeed(): print 'Try to fix the plugins and test them with PluginTest.py';sys.exit()

    client_s = itchat.storage.Storage()
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
        itchat.argparser.startCommandLine(client_s, client, msgList, front, cmdList)
