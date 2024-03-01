#!/usr/bin/env python

import smtplib
import os.path
import logging
import sys
import pkg_resources as pkg
from multiprocessing import Pool
from collections import deque, namedtuple

"""
Tool for sending email from python. It was created to notify
(hence, notipy :) me when a job was completed (along with any relevant results)
Compatible with both python2 and python3
"""

#To run:
#import notipymail.notipy as notipy
#notipy.sendMail("to@address.com", "This is a message")


# Constants
numMessageCharInLogEntry = 40
defaultSubject = "Notipy Automail"
logFileName = ""     # Overload at own risk
detailsFileName = "" # Overload at own risk

LogEntry = namedtuple("LogEntry", ['logLev', 'msg'])

class MissingValueException(Exception):
    pass

class MissingConfigFileException(Exception):
    pass

required_keywords = ["email", "password", "server", "port"]


def _readSendDetails():
    send_details = {}

    #sendDetails overridden from default by user
    if detailsFileName and os.path.isfile(detailsFileName): 
        fin = open(detailsFileName)
    elif pkg.resource_exists('notipymail', 'data/senddetails.dat'):
        fin = open(pkg.resource_filename('notipymail', 'data/senddetails.dat'), 'r')
    else:
        raise MissingConfigFileException()
    
    for line in fin:
        lineSplit = line.rstrip().split(":")
        send_details[lineSplit[0]] = lineSplit[1]
    
    fin.close()
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
    if isinstance(toAddress, str):   #smtplib expects the toAddress to be a list
        toAddress = [x.strip() for x in toAddress.split(",")]

    try:
        send_details = _readSendDetails()
    except MissingValueException as e:
        statusStr = "The sendDetails.dat file must contain a key and value for key: " + str(e) + " ."
        logCode = logging.ERROR
    except MissingConfigFileException as e:
        statusStr = "You must provide a sendDetails.dat file. See GitHub Readme for file format details."
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
            statusStr = "Successfully sent mail to " + str(toAddress) + " with message: " + message[:min(numMessageCharInLogEntry,len(message))].encode('string_escape')
            if len(message) > numMessageCharInLogEntry:
                statusStr += "..."

    return LogEntry(logLev=logCode, msg=statusStr)

def _logSend(result):
    logLevel = result.logLev
    message = result.msg

    if logLevel == logging.INFO:
        logging.info(message)
    elif logLevel == logging.ERROR:
        logging.error(message)

def sendMail(toAddress, message, subject = ""):
    if subject:
        status = _formatAndSendMail(toAddress, message, subject)
    else:
        status = _formatAndSendMail(toAddress, message)
    _logSend(status)

def sendMailAsync(toAddress, message, subject = ""):
    args = [toAddress, message]
    if subject:
        args.append(subject)
    pool = Pool()
    pool.apply_async(_formatAndSendMail, args, callback=_logSend)

def queryLog(numEntry, logFile=None, out=sys.stdout):
    if not logFile:
        logFile = logFileName
    with open(logFile) as fin:
        for i in deque(fin, maxlen=numEntry):
            out.write(i)

def clearLog(logFile=None):
    if not logFile:
        logFile = logFileName
    open(logFileName, 'w').close() # Clears the file

def updateSendDetails(uEmail = "", uPassword = "", uServer = "", uPort = ""):
    filename = ""
    if detailsFileName: #sendDetails overridden from default by user
        filename = detailsFileName
    else:
        filename = pkg.resource_filename('notipymail','data/senddetails.dat')

    fout = open(filename, 'w')

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

def clearSendDetails():
    updateSendDetails() # clears personal information from the sendDetails.dat file

# Run when notipy is imported
if not logFileName: # If the user hasn't overridden the log
    logFileName = pkg.resource_filename('notipymail', 'data/notipy.log')
logging.basicConfig(filename=logFileName, level=logging.DEBUG, format='%(asctime)-15s %(levelname)-8s %(message)s')