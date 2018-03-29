# FINAL VERSION OF 2.0
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt,QTimer, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QGridLayout,QDockWidget,QApplication,QWidget,QLabel, QVBoxLayout, QMainWindow
#from PyQt5.QtGui import QGridLayout
import time
import sys
'''
class MainWindow_V2(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow_V2,self).__init__(parent)

        #self.docker = QDockWidget(self)
        #self.docker.setAllowedAreas(Qt.RightDockWidgetArea)
        #self.docker.setWidget(TimeWidget(self))

        self.timeWidg = TimeWidget(self)
        self.timeWidg.move(600,30)
        self.timeWidg.setStyleSheet(".QLabel{ color:white ; background-color:black ; font-size:60px }")



class TimeWidget(QWidget):
    def __init__(self, parent=None):
        super(TimeWidget,self).__init__(parent)
        self.timeLabel = QLabel('Time',self)
        self.timeLabel.setAlignment(Qt.AlignCenter)
        #self.timeLabel.setStyleSheet("{font-size = 40px }")
        self.setLayout = QVBoxLayout(self)
        self.layout().addWidget(self.timeLabel)
        
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayTimer)
        self.timer.start()
        QApplication.processEvents()
        self.setGeometry(40,40,400,200)
        #self.setStyleSheet("background:black")

    def displayTimer(self):
        print("connected")
        timef =QTime.currentTime()
        print("middle")
        self.timeLabel.setText(timef.toString(Qt.ISODate))
        minuteTime = timef.minute()
        hourTime = timef.hour()
        secTime = timef.second()
        print(str(hourTime)+" : "+str(minuteTime))
        print("next")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow_V2()
    win.showFullScreen()
    sys.exit(app.exec_())
'''

    
    
now = QDate.currentDate()

print(now.toString(Qt.ISODate))
print(now.toString(Qt.DefaultLocaleLongDate))

datetime = QDateTime.currentDateTime()

print(datetime.toString())

timef =QTime.currentTime()

print(timef.toString(Qt.DefaultLocaleLongDate))
'''
while True:
    timef =QTime.currentTime()
    print(timef.toString(Qt.DefaultLocaleLongDate))
'''
