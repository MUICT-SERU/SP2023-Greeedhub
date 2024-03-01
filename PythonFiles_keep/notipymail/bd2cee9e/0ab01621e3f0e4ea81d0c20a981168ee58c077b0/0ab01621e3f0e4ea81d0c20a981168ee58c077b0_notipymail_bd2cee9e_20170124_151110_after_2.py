#!/usr/bin/env python

import notipylib.notipy as notipy
import unittest
from StringIO import StringIO # Is this still compatible with python3
import time

class TestUpdatingVariables(unittest.TestCase):
    fromAddr = "from@here.com"
    fromPwd = "pwd"
    emailSer = "smtp.dummy.com"
    emailPort = 25
    
    alternateSendDetailsPath = "dummy"
    
    def setUp(self):
        pass
        
    def checkSendDetailsFile(self, toAddr, fromAddr, emailSer, emailPort, filePath=""):
        # This will be used to check the raw sendDetails file to ensure it was generated correctly
        pass
        
    def test_updateSendDetails(self):
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        checkSendDetailsFile(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)

    def test_updateSendDetailsNonDefaultFile(self):
        notipy.detailsFileName = alternateSendDetailsPath
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        checkSendDetailsFile(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort, filePath=notipy.detailsFileName)
        # Cleanup
        notipy.detailsFileName = ""
        
    def test_readSendDetails(self):
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        x = notipy._readSendDetails()
        # Here, check that x values are correct
        
    def test_readSendDetailsNonDefaultFile(self):
        notipy.detailsFileName = alternateSendDetailsPath
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        x = notipy._readSendDetails()
        # Here, check that x values are correct
        notipy.detailsFileName = "" # Cleanup
        
    def test_readIncompleteSendDetails(self):
        # Force a sendDetails file (default location) with a missing value
        # Attempt to read (using readSendDetails) and look for MissingValueException
        pass
        # Clean up sendDetails File
        
    def test_readNoSendDetails(self):
        # Delete the sendDetails file and try reading it
        # Look for MissingConfigFileException
        pass
        # Reinstate file
        
    def test_clearSendDetails(self):
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        notipy.clearSendDetails()
        x = notipy._readSendDetails()
        # Make sure we get MissingValueExceptions
        # Also, manually read the file to make sure NO values in it
        
    def test_clearSendDetailsNonDefaultFile(self):
        notipy.detailsFileName = alternateSendDetailsPath
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        notipy.clearSendDetails()
        x = notipy._readSendDetails()
        # Make sure we get MissingValueExceptions
        # Also, manually read the file to make sure NO values in it
        notipy.detailsFileName = "" # Cleanup
        
    def test_logFileMissingValueException(self):
        # Make sure the log file correctly logs a MissingValueException
        # Including Error code
        pass
        
    def test_logFileMissingConfigFileException(self):
        # Make sure the log file correctly logs a MissingConfigFileException
        # Including Error Code
        pass
        
    def test_logFileSMTPException(self):
        # Make sure the log file correctly logs a SMTPException when it occurs
        pass
        
    def test_queryLogExcess(self):
        # Make sure queryLog behaves correctly when we query more items from
        # the log than there are
        pass
        
    def test_clearLog(self):
        # Make sure the log is cleared correctly
        pass
        
    def test_clearLogNonDefaultFile(self):
        # Make sure the log is cleared correctly when its in non-default location
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
    
    
    def setUp(self):
        import testutil        
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        
    def checkLogEntry(self, subject=False, multRecipients=False):
        # This will be used to check the contents in the log and make sure they're correct
        pass
    
    def test_sendMail(self):
        msg = self.msg + "test_sendMail"
        notipy.sendMail(self.toAddr, msg)
        out = StringIO()
        notipy.queryLog(1, out=out)
        output = out.getvalue().strip()
        self.checkLogEntry()
        notipy.clearLog()

    def test_sendMailWithSubj(self):
        msg = self.msg + "test_sendMailWithSubj"
        notipy.sendMail(self.toAddr, msg, self.sub)
        out = StringIO()
        notipy.queryLog(1, out=out)
        output = out.getvalue().strip()
        self.checkLogEntry(subject=True)
        notipy.clearLog()
        
    def test_sendMailWithMultipleRecipients(self):
        msg = self.msg + "test_sendMailWithMultipleRecipients"
        notipy.sendMail(self.toAddr+","+self.toAddr2, msg)
        out = StringIO()
        notipy.queryLog(1, out=out)
        output=out.getvalue().strip()
        self.checkLogEntry(multRecipients=True)
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