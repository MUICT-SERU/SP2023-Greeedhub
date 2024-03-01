import notipylib.notipy as notipy
import unittest
from StringIO import StringIO
import time
import multiprocessing

class TestSendingMail(unittest.TestCase):
    toAddr = "to@destination.com"
    msg = "Test Message "
    sub = "test_subject"
    
    fromAddr = "from@here.com"
    fromPwd = "pwd"
    emailSer = "smtp.dummy.com"
    emailPort = 25
    
    
    def setUp(self):
        import testutil        
        notipy.updateSendDetails(self.fromAddr, self.fromPwd, self.emailSer, self.emailPort)
        
    def checkLogEntry(self, subject=False):
        pass
    
    def test_sendMail(self):
        msg = self.msg + "test_sendMail"
        notipy.sendMail(self.toAddr, msg)
        out = StringIO()
        notipy.queryLog(1, out=out)
        output = out.getvalue().strip()
        print(output)
        self.checkLogEntry()
        notipy.clearLog()

    def test_sendMailWithSubj(self):
        msg = self.msg + "test_sendMailWithSubj"
        notipy.sendMail(self.toAddr, msg, self.sub)
        out = StringIO()
        notipy.queryLog(1, out=out)
        output = out.getvalue().strip()
        print(output)
        self.checkLogEntry(subject=True)
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