import feedparser
import time
import sys
import CONFIGURATION as UserNewsSettings

from PyQt5.QtCore import Qt,QThread,pyqtSignal,QObject
from PyQt5.QtWidgets import (QApplication, QGridLayout, QGroupBox, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QLineEdit)
from PyQt5.QtGui import QPainter, QColor, QPen


class STAR_NEWS(QObject):
    channelName_signal = pyqtSignal(str)
    entries_signal = pyqtSignal(str)
    finished =pyqtSignal()
    
    def __init__(self, parent=None):
        super(STAR_NEWS,self).__init__(parent)
        self.STAR_RSS = feedparser.parse(UserNewsSettings.NEWS_URL)

    def getData(self):
        self.get_Channel_Name()
        self.previousNewsTitle ="\n"  
        for posts in self.STAR_RSS.entries:
            #print(posts.title + '\n' + posts.description + "\n")
            self.currentNewsTitle = ">"+posts.title  
            self.previousNewsTitle = self.previousNewsTitle + '\n' + self.currentNewsTitle
            #self.entries_signal.emit(posts.title)
            #time.sleep(2)
        self.entries_signal.emit(self.previousNewsTitle)
        self.finished.emit()  

    def get_Channel_Name(self):
        title = self.STAR_RSS.feed.title
        self.channelName_signal.emit(title)


class NEWS_WIDGET(QWidget):
    def __init__(self, parent=None):
        super(NEWS_WIDGET,self).__init__(parent)

        self.grid = QGridLayout()
        
        self.verticalLayout = QVBoxLayout()

        self.oldNews = " "
        self.NewsChannelTitle = QLabel("CHANNEL NAME")
        self.NewsEntries = QLabel("DESCRITION")
        self.opt = QLabel("CLOSE BOTH EYES FOR 5 SEC TO BACK")
        self.work = STAR_NEWS()
        self.thread = QThread()
        
        self.work.channelName_signal.connect(self.updateChannelName)
        self.work.entries_signal.connect(self.updateNewsEntries)
        self.work.finished.connect(self._finished)
        self.work.moveToThread(self.thread)
        #self.work.finished.connect(self._finished)

        self.thread.started.connect(self.work.getData)


        self.NewsChannelTitle.setStyleSheet("color: white ; font: bold 20px")

        self.NewsEntries.setStyleSheet("color: white ; font: bold 12px")
        self.NewsEntries.setAlignment(Qt.AlignLeft)
        self.opt.setStyleSheet("color: white ; font: bold 14px")
        self.opt.setAlignment(Qt.AlignLeft)
        self.verticalLayout.addWidget(self.NewsChannelTitle)
        self.verticalLayout.addWidget(self.NewsEntries)
        self.verticalLayout.addWidget(self.opt)
        self.grid.addLayout(self.verticalLayout,1,1) 
                                    
        QApplication.processEvents()
                                  
        self.setLayout(self.grid)
        self.setWindowTitle("NEWS WIDGET")
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.black)
        self.setPalette(p)
        self.resize(400,300)
        
    def startNews(self):
        self.thread.start()
    
    def updateChannelName(self,channelName):
        self.NewsChannelTitle.setText(channelName)

    def updateNewsEntries(self,entriesType):
        self.NewsEntries.setText(entriesType)
       
    def _finished(self):
        print("[WEATHER WIDGET GUI STATUS] : FINISHED SIGNAL IS RECEIVED FROM EMAIL BACKEND")
        self.thread.quit()
        self.thread.wait()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    analysisWin = NEWS_WIDGET()
    analysisWin.startNews()
    analysisWin.show()
    sys.exit(app.exec_())


