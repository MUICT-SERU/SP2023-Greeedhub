#!/usr/bin/env python

# This code was adapted from code written by John Montgomery
# in his inspiring 2007 post on Monkey Patching
# http://www.psychicorigami.com/2007/09/20/monkey-patching-pythons-smtp-lib-for-unit-testing/

# monkey-patch smtplib so we don't send actual emails
import smtplib

inbox=[]


class Message(object):
    def __init__(self,from_address,to_address,fullmessage):
        self.from_address=from_address
        self.to_address=to_address
        self.fullmessage=fullmessage

class MonkeySMTP(object):
    def __init__(self,address,port):
        self.address=address
        self.port=port
        
    def starttls(self):
        pass

    def login(self,username,password):
        self.username=username
        self.password=password

    def sendmail(self,from_address,to_address,fullmessage):
        if 'raise smtpexception' in fullmessage:
            raise smtplib.SMTPException
        global inbox
        inbox.append(Message(from_address,to_address,fullmessage))

    def quit(self):
        self.has_quit=True

# this is the actual monkey patch (simply replacing one class with another)
smtplib.SMTP=MonkeySMTP