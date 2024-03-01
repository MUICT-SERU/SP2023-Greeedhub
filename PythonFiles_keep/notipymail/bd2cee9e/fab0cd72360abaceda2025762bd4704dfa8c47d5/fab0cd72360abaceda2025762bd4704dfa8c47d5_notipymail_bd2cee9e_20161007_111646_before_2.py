#!/usr/bin/env python

import smtplib
import os.path

"""
Short script for sending email from python. It was created to notify
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


def readSendDetails():
    required_keywords = ["email", "password", "server", "port"]
    # send_details = {"email": "", "password": "", "server": "", "port": ""}
    send_details = {}

    # Always check for sendDetails1.txt. This is so the user can have a
    # file containing email and password that is NOT tracked by Git.
    if os.path.isfile("sendDetails1.txt"):
        fin = open("sendDetails1.txt")

    elif os.path.isfile("sendDetails.txt"):
        fin = open("sendDetails.txt")

    else:
        print("You must provide a sendDetails.txt/sendDetails1.txt file")
        print("See BitBucket for file format details.")


    for line in fin:
        lineSplit = line.rstrip().split(":")
        send_details[lineSplit[0]] = lineSplit[1]

    # Check for required terms
    for i in required_keywords:
        if i in send_details.keys():
            if not send_details[i]:
                raise Exception([i])
        else:
            raise Exception(i)

    return send_details



def sendMail(toAddress, message, subject="NB AutoMail"):

    if isinstance(toAddress, str):   #smtolib expects the toAddress to be a string
        toAddress = [x.strip() for x in toAddress.split(",")]

    try:
        send_details = readSendDetails()
    except Exception as e:
        print ("ERROR: The sendDetails.txt/sendDetails1.txt file must contain a key and value for key: ")
        print (e)
        return -1

    SERVER = send_details["server"]
    PORT = send_details["port"]
    FROM = send_details["email"]
    PWD = send_details["password"]

    fullMessage = """From: %s\r\nTo: %s\r\nSubject: %s\r\n\

    %s
    """ % (FROM, ", ".join(toAddress), subject, message )

    server = smtplib.SMTP(SERVER, PORT)
    server.starttls()
    server.login(FROM, PWD)

    server.sendmail(FROM, toAddress, fullMessage)
    server.quit()

    return 0


# Feature ToDo list
# Secure local password storage
# More robust error checking and handling
# Error log to preserve any encountered issues (such as server down time after hours)
# Asynchronous send