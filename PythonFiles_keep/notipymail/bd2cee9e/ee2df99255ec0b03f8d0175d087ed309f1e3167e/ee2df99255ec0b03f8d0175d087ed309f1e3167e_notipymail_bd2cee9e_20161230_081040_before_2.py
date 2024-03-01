#!/usr/bin/env python

import smtplib
import os.path
import logging
import pkg_resources as pkg
from multiprocessing import Pool
from collections import deque, namedtuple

"""
Tool for sending email from python. It was created to notify
(hence, notipy :) me when a job was completed (along with any relevant results)
Compatible with both python2 and python3
"""

#Instructions:
#Create file <<< sendDetails1.txt >> containing the following contents 
#
#email:nbauto791@gmail.com
#password:<redacted>
#server:smtp.gmail.com
#port:587
#
#To run:
#import notipy
#notipy.sendMail("to@address.com", "This is a message")


# Constants
numMessageCharInLogEntry = 40
defaultSubject = "Notipy Automail"
logFileName = "notipy.log"
detailsFileName = ""

class MissingValueException(Exception):
    pass

class MissingConfigFileException(Exception):
    pass

required_keywords = ["email", "password", "server", "port"]

def _readSendDetails():
    send_details = {}

    # Check for sendDetails1.txt. This is included in the .gitignore
    # file containing so it is NOT tracked by Git.
    if detailsFileName and os.path.isfile(detailsFileName):
        fin = open(detailsFileName)
    elif pkg.resource_exists('notipylib', 'data/senddetails.dat'):
        fin = open(pkg.resource_filename('notipylib', 'data/senddetails.dat'), 'r')
    else:
        raise MissingConfigFileException()

    for line in fin:
        lineSplit = line.rstrip().split(":")
        send_details[lineSplit[0]] = lineSplit[1]

    # Check for required terms
    for i in required_keywords:
        if i in send_details.keys():
            if not send_details[i]:
                raise MissingValueException(i)
        else:
            raise MissingValueException(i)
    return send_details

def _formatAndSendMail(toAddress, message, subject=defaultSubject):
    statusStr= ""
    logCode = logging.INFO
    if isinstance(toAddress, str):   #smtolib expects the toAddress to be a string
        toAddress = [x.strip() for x in toAddress.split(",")]

    try:
        send_details = _readSendDetails()
    except MissingValueException as e:
        statusStr = "The sendDetails1.txt file must contain a key and value for key: " + str(e) + " ."
        logCode = logging.ERROR
    except MissingConfigFileException as e:
        statusStr = "You must provide a sendDetails1.txt file. See GitHub Readme for file format details."
        logCode = logging.ERROR
    else:
        SERVER = send_details["server"]
        PORT = send_details["port"]
        FROM = send_details["email"]
        PWD = send_details["password"]

        fullMessage = """From: %s\r\nTo: %s\r\nSubject: %s\r\n\

        %s
        """ % (FROM, ", ".join(toAddress), subject, message )

        try:
            server = smtplib.SMTP(SERVER, PORT)
            server.starttls()
            server.login(FROM, PWD)
            server.sendmail(FROM, toAddress, fullMessage)
            server.quit()
        except smtplib.SMTPException as e:
            statusStr = "SMTPException caught: " + str(e)
            logCode = logging.ERROR
        else:
            statusStr = "Successfully sent mail to " + str(toAddress) + " with message: " + message[:min(numMessageCharInLogEntry,len(message))] + "..."

    return logEntry(level=logCode, msg=statusStr)

def _logSend(result):
    message = result.msg
    logLevel = result.level
    if logLevel == logging.INFO:
        logging.info(message)
    elif logLevel == logging.ERROR:
        logging.error(message)

def sendMail(toAddress, message, subject = ""):
    if (subject != ""):
        status = _formatAndSendMail(toAddress, message, subject)
    else:
        status = _formatAndSendMail(toAddress, message)
    _logSend(status)

def sendMailAsync(toAddress, message, subject = ""):
    args = [toAddress, message]
    if (subject != ""):
        args.append(subject)
    pool = Pool()
    pool.apply_async(_formatAndSendMail, args, callback=_logSend)

def queryLog(numEntry, logFile=None):
    if not logFile:
        logFile = logFileName
    with open(logFile) as fin:
        for i in deque(fin, maxlen=numEntry):
            print(i)

def updateSendDetails(uEmail, uPassword, uServer, uPort):
    if detailsFileName: # sendDetails overriden from default file in data/*.dat
        fout = open(detailsFileName, "w")
    else:
        fout = open(pkg.resource_filename('notipylib','data/senddetails.dat'), 'w')
        
    for i in required_keywords:
        value = ""
        if i == "email":
            value = uEmail
        elif i == "password":
            value = uPassword
        elif i == "server":
            value = uServer
        elif i == "port":
            value = uPort
        fout.write('{0}:{1}\n'.format(i, value))
    fout.close()

# Run when notipy is imported
logging.basicConfig(filename=logFileName, level=logging.DEBUG, format='%(asctime)-15s %(levelname)-8s %(message)s')
logEntry = namedtuple("LogEntry", ['level','msg'])