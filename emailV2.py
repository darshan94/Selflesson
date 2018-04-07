#   CREATED BY DARSHAN
#   DATE : 2AM 20 MARCH
#   PURPOSE : DEVELOP GUI FOR EMAIL
#   MODULE EMAIL E1.0
#   MAIN WINDOW FOR EMAIL MODULE

from PyQt5.QtCore import Qt,QThread,pyqtSignal,QObject
from PyQt5.QtWidgets import (QApplication, QGridLayout, QGroupBox, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QLineEdit)
from PyQt5.QtGui import QPainter, QColor, QPen



import imaplib
import time
import uuid
import email
import datetime

class EMAIL_BACKEND(QObject):

    signal_Email_Name = pyqtSignal(str)
    signal_Email_Notifications_Num = pyqtSignal(int)
    emailLoader_finished = pyqtSignal()

    def __init__(self):
        super(EMAIL_BACKEND,self).__init__()
        print("[INFO - EMAIL_BACKEND ] : EMAIL_BACKEND CONSTRUCTOR HAS BEEN CALLED")
        self.ORG_EMAIL   = "@gmail.com"
        self.FROM_EMAIL  = "drviruz94" + self.ORG_EMAIL
        self.FROM_PWD    = "94revenge"
        self.SMTP_SERVER = "imap.gmail.com"
        self.SMTP_PORT   = 993
        print("[INFO - EMAIL_BACKEND ] : EMAIL_BACKEND CONSTRUCTOR INIATIATED")

    def __del__(self):
        self.wait()

    def emailExtractor(self):
        print("[INFO - EMAIL_BACKEND ] : EMAIL_BACKEND RUN() CALLED")
        try:
            print("[INFO - EMAIL_BACKEND ] : LOGIN PROCESS BEGAN")
            self.mail = imaplib.IMAP4_SSL(self.SMTP_SERVER)
            self.mail.login(self.FROM_EMAIL,self.FROM_PWD)
            self.mail.list()
            print("[INFO - EMAIL_BACKEND ] : LOGGED IN")
            
            self.mail.select('inbox')
            print("[INFO - EMAIL_BACKEND ] : INBOX ACCESSED")
            date = (datetime.date.today() - datetime.timedelta(1)).strftime("%d-%b-%Y")
            print("[INFO - EMAIL_BACKEND ] : FILTERING EMAIL RECEIVED DATE")
            type, self.data = self.mail.search(None, 'ALL','(SENTSINCE {date})'.format(date=date))
            print("[INFO - EMAIL_BACKEND ] : MAILS FILTERED")
            self.mail_ids = self.data[0]
            print("[INFO - EMAIL_BACKEND ] : ID MAILS EXTRACTED")
            self.id_list = self.mail_ids.split()
            print("[INFO - EMAIL_BACKEND ] : ID MAILS EXTRACTED PART 2")
            self.num = len(self.id_list)
            print("[INFO - EMAIL_BACKEND ] : ID MAILS EXTRACTED PART 2")
            self.user = "Hi Drviruz"
            print("[INFO - EMAIL_BACKEND ] : OBTAINED USER NAME")
            self.signal_Email_Name.emit(self.user)
            print("[INFO - EMAIL_BACKEND ] : USER NAME SIGNAL FROM EMAIL BACKEND SENT")
            self.signal_Email_Notifications_Num.emit(self.num)
            print("[INFO - EMAIL_BACKEND ] : EMAIL NOTIFICATION SIGNAL FROM EMAIL BACKEND SENT")
            self.emailLoader_finished.emit()
            print("[INFO - EMAIL_BACKEND ] : FINISH SIGNAL FROM EMAIL BACKEND SENT")
        
        except OSError as e:
            print (str(e))

    
class emailWidget(QWidget):

    done_Signal = pyqtSignal()
   
    def __init__(self, parent=None):
        super(emailWidget,self).__init__(parent)
        print("[INFO - EMAIL_WIDGET ] : EMAIL WIDGET INITIALIZATION CALLED")

        self.finished_status = False
               
        grid = QGridLayout()

        self.emailBox=QGroupBox("EMAIL SECTION")
        self.title = QLabel("LOADING")
        self.mainContent = QLabel("LOADING")
        self.opt_1 = QLabel("CLOSE LEFT EYES FOR 5 SEC TO OPEN EMAILS")
        self.opt_2 = QLabel("CLOSE BOTH EYES FOR 5 SEC TO BACK")
        self.opt_debug = QLabel("STATUS : LOADING")
        

        self.title.setStyleSheet("color: white")
        self.title.setAlignment(Qt.AlignCenter)
        self.mainContent.setStyleSheet("color: white ; font: bold 20px")
        self.mainContent.setAlignment(Qt.AlignCenter)
        self.opt_1.setStyleSheet("color: white ;font: bold 12px")
        self.opt_1.setAlignment(Qt.AlignLeft)
        self.opt_2.setStyleSheet("color: white ;font: bold 12px")
        self.opt_2.setAlignment(Qt.AlignLeft)
        self.opt_debug.setStyleSheet("color: white ;font: bold 12px")
        self.opt_debug.setAlignment(Qt.AlignLeft)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout_Option = QVBoxLayout()
        
        self.combiner = QVBoxLayout()
        
        self.verticalLayout.addWidget(self.title)
        self.verticalLayout.addWidget(self.mainContent)

        self.verticalLayout_Option.addWidget(self.opt_1)
        self.verticalLayout_Option.addWidget(self.opt_2)
        self.verticalLayout_Option.addWidget(self.opt_debug)

        self.verticalLayout.addStretch(1)
        self.verticalLayout_Option.addStretch(1)
        
        
        self.combiner.addLayout(self.verticalLayout)
        self.combiner.addLayout(self.verticalLayout_Option)
        self.combiner.addStretch(0)
        self.emailBox.setLayout(self.combiner)
        
        grid.addWidget(self.emailBox,1,1)


        self.emailWorker = EMAIL_BACKEND()
        self.emailthread = QThread()
        self.emailWorker.signal_Email_Name.connect(self.updateDate)
        self.emailWorker.signal_Email_Notifications_Num.connect(self.updateNotification)
        self.emailWorker.emailLoader_finished.connect(self._finished)
        self.emailWorker.moveToThread(self.emailthread)
        self.emailthread.started.connect(self.emailWorker.emailExtractor)
        #self.emailthread.start()

        
        
        QApplication.processEvents()
        self.setLayout(grid)
        self.setWindowTitle("EMAIL MODULE")

        #set window background color
        
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)
        self.resize(400,300)
        #self.

    def startEmailBackend(self):
        self.show()
        self.emailthread.start()

    def updateDate(self,value):
        print("[EMAIL WIDGET GUI STATUS] : USER NAME SIGNAL IS RECEIVED FROM EMAIL BACKEND")
        self.title.setText(str(value))

    def updateNotification(self,notificationNo):
        print("[EMAIL WIDGET GUI STATUS] : EMAIL NOTIFICATION SIGNAL IS RECEIVED FROM EMAIL BACKEND")
        self.mainContent.setText(" YOU HAVE " + str(notificationNo) + " MAILS")

    
    def _finished(self):
        print("[EMAIL WIDGET GUI STATUS] : FINISHED SIGNAL IS RECEIVED FROM EMAIL BACKEND")
        self.emailthread.quit()
        self.emailthread.wait()

        self.finished_status = True
        self.opt_debug.setText(str(self.finished_status))
        self.done_Signal.emit()

    def email_status(self):
        print("[EMAIL WIDGET GUI STATUS] : email_status(self) IS CALLED " + str(self.finished_status))
        return self.finished_status

    

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    analysisWin = emailWidget()
    analysisWin.setVisible(0)
    #analysisWin.showFullScreen()
    sys.exit(app.exec_())
