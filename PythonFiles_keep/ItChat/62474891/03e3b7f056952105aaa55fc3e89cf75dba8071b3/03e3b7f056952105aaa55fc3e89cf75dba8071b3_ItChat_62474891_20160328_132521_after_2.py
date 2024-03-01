import time, thread
from client import client

import traceback

__version__ = '0.1b'

__client = client()
def auto_login(): return __client.auto_login()
# The following method are all included in auto_login >>>
def get_QRuuid(): return __client.get_QRuuid()
def get_QR(): return __client.get_QR()
def check_login(): return __client.check_login()
def web_init(): return __client.web_init()
def get_batch_contract(groupUserName): return __client.get_batch_contract(groupUserName)
def get_contract(): return __client.get_contract()
def show_mobile_login(): return __client.show_mobile_login()
def start_receiving(): return __client.start_receiving()
# <<<
def send_msg(toUserName = None, msg = 'Test Message'): return __client.send_msg(toUserName, msg)
def send_file(fileDir, toUserName): return __client.send_file(fileDir, toUserName)
def send_img(fileDir, toUserName): return __client.send_img(fileDir, toUserName)
def add_friend(Status, UserName, Ticket): return __client.add_friend(Status, UserName, Ticket)
def create_chatroom(memberList, topic = ''): return __client.create_chatroom(memberList, topic)
def delete_member_from_chatroom(chatRoomUserName, memberList): return __client.delete_member_from_chatroom(chatRoomUserName, memberList)
def add_member_into_chatroom(chatRoomUserName, memberList): return __client.add_member_into_chatroom(chatRoomUserName, memberList)
def send(msg = 'Test Message', toUserName = None):
    if msg is None: return
    if msg[:5] == '@fil@':
        return __client.send_file(msg[5:], toUserName)
    elif msg[:5] == '@img@':
        return __client.send_image(msg[5:], toUserName)
    elif msg[:5] == '@msg@':
        return __client.send_msg(toUserName, msg[5:])
    else:
        return __client.send_msg(toUserName, msg)

# decorations
__functionDict = {'GroupChat': {}}
def configured_reply():
    try:
        msg = __client.storageClass.msgList.pop()
        if msg.get('GroupUserName') is None:
            __functionDict[msg['Type']](msg)
        else:
            __functionDict['GroupChat'][msg['Type']](msg)
    except:
        pass

def msg_dealer(_type = None, *args, **kwargs):
    if hasattr(_type, '__call__'):
        fn = _type
        def _msg_dealer(*args, **kwargs):
            try:
                msg = __client.storageClass.msgList.pop()
                send(fn(msg, *args, **kwargs), None if msg is None else msg.get('FromUserName', None))
            except:
                pass
        print('Reply function has been set, call %s to reply one message'%fn.__name__)
        return _msg_dealer
    elif _type is None:
        return configured_reply
    else:
        if not isinstance(_type, list): _type = [_type]
        def _msg_dealer(fn, *_args, **_kwargs):
            for msgType in _type:
                if kwargs.get('isGroupChat', False):
                    __functionDict['GroupChat'][msgType] = fn
                else:
                    __functionDict[msgType] = fn
        return _msg_dealer

# in-build run
def run():
    print('Start auto replying')
    while 1:
        configured_reply()
        time.sleep(.3)

