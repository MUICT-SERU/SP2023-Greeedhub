#!/usr/bin/env python

"""notipy.py: A tool for sending emails from python.

    Notipy was created to notify (hence, notipy :) me when a job was completed
    (along with any relevant results). It is compatible with both python2 and
    python3.

    To run (also see Readme.md):
    >import notipymail.notipy as notipy
    >notipy.sendMail("to@address.com", "This is a message")

    File name: notipy.py
    Author: Nathaniel Bryans
    Date created: 2016-09-15
    Date last modified: 2017-06-22
    Python versions: 2.7 & 3.6
"""

import smtplib
import os.path
import logging
import sys
import pkg_resources as pkg
from multiprocessing import Pool
from collections import deque, namedtuple


# Constants
numMessageCharInLogEntry = 40 # Length of message to include in log
defaultSubject = 'Notipy Automail'
logFileName = ''       # Overload for non-default filename (default: notipy.log)
detailsFileName = '' # Overload to change file storing email details


# Definitions
LogEntry = namedtuple("LogEntry", ['logLev', 'msg'])

class MissingValueException(Exception):
    pass

class MissingConfigFileException(Exception):
    pass

required_keywords = ['email', 'password', 'server', 'port']


# Methods
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
    for keyword in required_keywords:
        if keyword in send_details.keys():
            if not send_details[keyword]:
                raise MissingValueException(keyword) # Missing value of required keyword
        else:
            raise MissingValueException(keyword)     # Missing required keyword

    return send_details


def _formatAndSendMail(toAddress, message, subject=defaultSubject):
    statusStr= ""
    logCode = logging.INFO

    if isinstance(toAddress, str):   #smtplib expects the toAddress to be a list, not comma delimited
        toAddress = [x.strip() for x in toAddress.split(',')]

    try:
        send_details = _readSendDetails()
    except MissingValueException as e:
        statusStr = 'The sendDetails.dat file must contain a key and value for key: ' + str(e) + ' .'
        logCode = logging.ERROR
    except MissingConfigFileException as e:
        statusStr = 'You must provide a sendDetails.dat file. See Readme for file format details.'
        logCode = logging.ERROR
    else:
        SERVER = send_details['server']
        PORT = send_details['port']
        FROM = send_details['email']
        PWD = send_details['password']

        # Format message (including meta data), note the white space
        fullMessage = """From: %s\r\nTo: %s\r\nSubject: %s\r\n\

        %s
        """ % (FROM, ', '.join(toAddress), subject, message )

        try:
            server = smtplib.SMTP(SERVER, PORT)
            server.starttls()
            server.login(FROM, PWD)
            server.sendmail(FROM, toAddress, fullMessage)
            server.quit()
        except smtplib.SMTPException as e:
            statusStr = 'SMTPException caught: ' + str(e)
            logCode = logging.ERROR
        else:
            statusStr = 'Successfully sent mail to ' + str(toAddress) + ' with message: ' + message[:min(numMessageCharInLogEntry,len(message))].encode('string_escape')
            if len(message) > numMessageCharInLogEntry:
                statusStr += '...'

    return LogEntry(logLev=logCode, msg=statusStr)


def _logSend(result):
    logLevel = result.logLev
    message = result.msg

    if logLevel == logging.INFO:
        logging.info(message)
    elif logLevel == logging.ERROR:
        logging.error(message)


def sendMail(toAddress, message, subject = ''):
    """Send an email. This can take a few seconds.

    Required arguments:
    toAddress -- the email address(es) of the recipient
    message -- A string containing the email message

    Keyword arguments:
    subject -- An optional string with the email subject (default 'Notipy Automail')
    """

    if subject:
        status = _formatAndSendMail(toAddress, message, subject)
    else:
        status = _formatAndSendMail(toAddress, message)
    _logSend(status)


def sendMailAsync(toAddress, message, subject = ''):
    """Send an email asynchronously.

    Required arguments:
    toAddress -- the email address(es) of the recipient
    message -- A string containing the email message

    Keyword arguments:
    subject -- An optional string with the email subject (default 'Notipy Automail')
    """

    args = [toAddress, message]
    if subject:
        args.append(subject)
    pool = Pool()
    pool.apply_async(_formatAndSendMail, args, callback=_logSend)


def queryLog(numEntry, logFile=None, out=sys.stdout):
    """Query the log entries for the last emails sent.

    Required arguments:
    numEntry -- the number of log entries to return

    Keyword arguments:
    logFile -- The filename if using a log file other than the default
    out -- Where to display the results (useful for testing)
    """

    if not logFile:
        logFile = logFileName
    with open(logFile) as fin:
        for i in deque(fin, maxlen=numEntry):
            out.write(i)


def clearLog(logFile=None):
    """Clear all entries in the log file. Useful for testing.

    Required arguments:
    logFile -- The filename if using a log file other than the default
    """

    if not logFile:
        logFile = logFileName
    open(logFileName, 'w').close() # Clears the file


def updateSendDetails(uEmail = '', uPassword = '', uServer = '', uPort = ''):
    """Update the sender's details.

    Keyword arguments:
    uEmail -- The sender's email address
    uPassword -- The sender's email password
    uServer -- The address of the sender's outgoing server
    uPort -- The port for the sender's outgoing server
    """

    filename = ""
    if detailsFileName: #sendDetails overridden from default by user
        filename = detailsFileName
    else:
        filename = pkg.resource_filename('notipymail','data/senddetails.dat')

    fout = open(filename, 'w')

    for i in required_keywords:
        value = ''
        if i == 'email':
            value = uEmail
        elif i == 'password':
            value = uPassword
        elif i == 'server':
            value = uServer
        elif i == 'port':
            value = uPort
        fout.write('{0}:{1}\n'.format(i, value))
    fout.close()


def clearSendDetails():
    """clears the sender's details."""
    updateSendDetails()


# This is run when notipy.py is imported, sets up the log
if not logFileName: # If the user hasn't overridden the log
    logFileName = pkg.resource_filename('notipymail', 'data/notipy.log')
logging.basicConfig(filename=logFileName, level=logging.DEBUG, format='%(asctime)-15s %(levelname)-8s %(message)s')