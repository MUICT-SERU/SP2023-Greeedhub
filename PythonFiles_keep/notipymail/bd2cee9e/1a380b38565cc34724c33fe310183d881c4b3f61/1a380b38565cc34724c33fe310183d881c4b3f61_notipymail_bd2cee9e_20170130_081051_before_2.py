#!/usr/bin/env python

import notipymail.notipy as notipy
import unittest
import time
import os
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

class TestUpdating(unittest.TestCase): 
    toAddr = "to@destination.com"
    toAddr2 = "to2@destination2.com"
    msg = "Test Message "
    sub = "test_subject"

    fromAddr = "from@here.com"
    fromPwd = "pwd"
    emailSer = "smtp.dummy.com"
    emailPort = 25

    alternateSendDetailsPath = "dummy.dat"

    @classmethod
    def setUpClass(self):
        import testutil
        self.alternateSendDetailsPath = os.getcwd()+ "\\" + self.alternateSendDetailsPath
        self.required_keywords = notipy.required_keywords

    @classmethod
    def tearDownClass(self):
        import smtplib
        # Delete dummy sendDetails file

    def checkSendDetailsFile(self, toAddr, fromAddr, emailSer, emailPort, filePath=""):
        if filePath == "":
            filePath = notipy.pkg.resource_filename('notipymail','data/senddetails.dat')

        assert os.path.exists(filePath)

        with open(filePath) as fin:
            for line in fin:
                x = line.split(':')
                self.assertTrue(len(x) == 2)
                x[0] = x[0].strip()
                self.assertTrue(x[0] in self.required_keywords)
                shouldEqual = ""
                if x[0] == 'email':
                    shouldEqual = self.fromAddr
                elif x[0] == 'password':
                    shouldEqual = self.fromPwd
                elif x[0] == 'server':
                    shouldEqual = self.emailSer
                elif x[0] == 'port':
                    shouldEqual = str(self.emailPort)
                self.assertTrue(x[1].strip() == shouldEqual)

    def checkReadSendDetailsDict(self, readDict):
        for i in self.required_keywords:
            self.assertTrue(i in readDict.keys())
            if i == 'email':
                shouldEqual = self.fromAddr
            elif i == 'password':
                shouldEqual = self.fromPwd
            elif i == 'server':
                shouldEqual = self.emailSer
            elif i == 'port':
                shouldEqual = str(self.emailPort)
            self.assertTrue(readDict[i] == shouldEqual)
    def checkSendDetailsClear(self, filename):
        # Make sure we get MissingValueExceptions
        self.assertRaises(notipy.MissingValueException, notipy._readSendDetails)

        # Also, manually read the file to make sure NO values in it
        with open(filename, 'r') as fin:
            for line in fin:
                x = line.rstrip().split(':')
                self.assertTrue(len(x[1]) == 0)
    def checkLogEntry(self, entry, missValExcp=False, missConfigExcp=False, smtpExcp=False):
        # This will be used to check the contents in the log and make sure they're correct
        if missValExcp or missConfigExcp or smtpExcp:
            self.assertTrue("ERROR" in entry)
            if missValExcp:
                self.assertTrue("file must contain a key and value" in entry)
            elif missConfigExcp:
                self.assertTrue("You must provide a" in entry)
            elif smtpExcp:
                self.assertTrue("SMTPException caught" in entry)

    def checkLogMultiLine(self, entry, numLineQueried, numLineActual):
        numNewLine = entry.count('\n')
        self.assertTrue(numNewLine <= 2)

    def test_updateSendDetails(self):
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        self.checkSendDetailsFile(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)

    def test_updateSendDetailsNonDefaultFile(self):
        notipy.detailsFileName = self.alternateSendDetailsPath
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        self.checkSendDetailsFile(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort, filePath=notipy.detailsFileName)
        notipy.detailsFileName = "" # Cleanup

    def test_readSendDetails(self):
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        x = notipy._readSendDetails()
        self.checkReadSendDetailsDict(x)
        
    def test_readSendDetailsNonDefaultFile(self):
        notipy.detailsFileName = self.alternateSendDetailsPath
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        x = notipy._readSendDetails()
        self.checkReadSendDetailsDict(x)
        notipy.detailsFileName = "" # Cleanup

    def test_readIncompleteSendDetails(self):
        filePath = notipy.pkg.resource_filename('notipymail','data/senddetails.dat')

        # Checking for exception with empty port value
        with open(filePath, 'w') as fin:
            fin.write('email:'+self.fromAddr+'\n')
            fin.write('password:'+self.fromPwd+'\n')
            fin.write('server:'+self.emailSer+'\n')
            fin.write('port:\n')
        self.assertRaises(notipy.MissingValueException, notipy._readSendDetails)

        # Checking for exception with missing pwd
        with open(filePath, 'w') as fin:
            fin.write('email:'+self.fromAddr+'\n')
            fin.write('server:'+self.emailSer+'\n')
            fin.write('port:'+str(self.emailPort)+'\n')
        self.assertRaises(notipy.MissingValueException, notipy._readSendDetails)

        #Cleanup
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)

    def test_readNoSendDetails(self):
        filePath = notipy.pkg.resource_filename('notipymail','data/senddetails.dat')

        os.remove(filePath)
        self.assertRaises(notipy.MissingConfigFileException, notipy._readSendDetails)

        #Cleanup
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)

    def test_clearSendDetails(self):
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        notipy.clearSendDetails()

        filePath = notipy.pkg.resource_filename('notipymail','data/senddetails.dat')
        self.checkSendDetailsClear(filePath)

        #Cleanup
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)

    def test_clearSendDetailsNonDefaultFile(self):
        notipy.detailsFileName = self.alternateSendDetailsPath
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        notipy.clearSendDetails()

        self.checkSendDetailsClear(notipy.detailsFileName)

        notipy.detailsFileName = "" # Cleanup

    def test_logFileMissingValueException(self):
        # Ensure the log file correctly logs a MissingValueException

        # Generate the Exception
        filePath = notipy.pkg.resource_filename('notipymail','data/senddetails.dat')
        # Checking for exception with missing pwd
        with open(filePath, 'w') as fin:
            fin.write('email:'+self.fromAddr+'\n')
            fin.write('server:'+self.emailSer+'\n')
            fin.write('port:'+str(self.emailPort)+'\n')

        notipy.sendMail(self.toAddr, self.msg)
        out = StringIO()
        notipy.queryLog(1, out=out)
        output=out.getvalue().strip()
        self.checkLogEntry(output, missValExcp=True)
        notipy.clearLog() # Cleanup

    def test_logFileMissingConfigFileException(self):
        # Ensure the log file correctly logs a MissingConfigFileException

        filePath = notipy.pkg.resource_filename('notipymail','data/senddetails.dat')
        os.remove(filePath)

        notipy.sendMail(self.toAddr, self.msg)

        out = StringIO()
        notipy.queryLog(1, out=out)
        output=out.getvalue().strip()
        self.checkLogEntry(output, missConfigExcp=True)
        notipy.clearLog() # Cleanup

    def test_logFileSMTPException(self):
        # Make sure the log file correctly logs a SMTPException when it occurs

        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)

        notipy.sendMail(self.toAddr, 'raise smtpexception')

        out = StringIO()
        notipy.queryLog(1, out=out)
        output=out.getvalue().strip()
        self.checkLogEntry(output, smtpExcp=True)
        notipy.clearLog()


    def test_queryLogExcess(self):
        # Make sure queryLog behaves correctly when we query more items from
        # the log than there are
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        notipy.clearLog()
        notipy.sendMail(self.toAddr, self.msg)
        notipy.sendMail(self.toAddr, self.msg)

        out = StringIO()
        notipy.queryLog(3, out=out)
        output=out.getvalue().strip()

        self.checkLogMultiLine(output, 3, 2)
        notipy.clearLog()

    def test_clearLog(self):
        # Make sure the log is cleared correctly
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)

        notipy.sendMail(self.toAddr, self.msg)
        notipy.sendMail(self.toAddr, self.msg)

        notipy.clearLog()

        #Verify (manually) here that the log is cleared
        filePath = notipy.pkg.resource_filename('notipymail','data/notipy.log')
        self.assertTrue(os.stat(filePath).st_size == 0)

    def test_clearLogNonDefaultFile(self):
        # Make sure the log is cleared correctly when its in non-default location
        
        # Right now, to test this I need to change file name in notipy.py
        # and reload module. Change program behaviour to make this easier
        # to test
        pass


class TestSendingMail(unittest.TestCase):
    toAddr = "to@destination.com"
    toAddr2 = "to2@destination2.com"
    msg = "Test Message "
    sub = "test_subject"

    fromAddr = "from@here.com"
    fromPwd = "pwd"
    emailSer = "smtp.dummy.com"
    emailPort = 25

    @classmethod
    def setUpClass(self):
        import testutil        
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)

    @classmethod
    def tearDownClass(self):
        import smtplib # Clear Monkey Patch on smtplib
        notipy.clearSendDetails()

    def checkLogEntry(self, entry, subject=False, multRecipients=False):
        # This will be used to check the contents in the log and make sure they're correct
        self.assertTrue("Successfully sent mail to" in entry)
        self.assertTrue("INFO" in entry)
        self.assertTrue(self.toAddr in entry)
        if multRecipients:
            self.assertTrue(self.toAddr2 in entry)

    def test_sendMail(self):
        msg = self.msg + "test_sendMail"
        notipy.sendMail(self.toAddr, msg)
        out = StringIO()
        notipy.queryLog(1, out=out)
        output = out.getvalue().strip()
        self.checkLogEntry(output)
        notipy.clearLog()

    def test_sendMailWithSubj(self):
        msg = self.msg + "test_sendMailWithSubj"
        notipy.sendMail(self.toAddr, msg, self.sub)
        out = StringIO()
        notipy.queryLog(1, out=out)
        output = out.getvalue().strip()
        self.checkLogEntry(output, subject=True)
        notipy.clearLog()

    def test_sendMailWithMultipleRecipients(self):
        msg = self.msg + "test_sendMailWithMultipleRecipients"
        notipy.sendMail(self.toAddr+","+self.toAddr2, msg)
        out = StringIO()
        notipy.queryLog(1, out=out)
        output=out.getvalue().strip()
        self.checkLogEntry(output, multRecipients=True)
        notipy.clearLog()

    # Unsure how to test Async function at this time since
    # Monkey patch on the smtplib.SMTP does not carry over to
    # spawned processes
    
    # def test_sendMailAsync(self):
        # msg = self.msg + "test_sendMailAsync"
        # notipy.sendMailAsync(self.toAddr, msg)
        # time.sleep(5)
        # out = StringIO()
        # notipy.queryLog(1, out=out)
        # output = out.getvalue().strip()
        # print(output)
        # self.checkLogEntry()
        # notipy.clearLog()
        
    # def test_sendMailAsyncWithSubj(self):
        # msg = self.msg + "test_sendMailAsyncWithSubj"
        # notipy.sendMailAsync(self.toAddr, msg, self.sub)
        # time.sleep(5)
        # out = StringIO()
        # notipy.queryLog(1, out=out)
        # output = out.getvalue().strip()
        # print(output)
        # self.checkLogEntry(subject=True)
        # notipy.clearLog()

if __name__ == '__main__':
    unittest.main()