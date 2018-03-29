# FINAL VERSION OF 2.0
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt,QTimer, pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QGridLayout,QDockWidget,QApplication,QWidget,QLabel, QVBoxLayout, QMainWindow
import time
import sys

class MainWindow_V2(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow_V2,self).__init__(parent)

        #self.docker = QDockWidget(self)
        #self.docker.setAllowedAreas(Qt.RightDockWidgetArea)
        #self.docker.setWidget(TimeWidget(self))

        self.timeWidg = TimeWidget(self)
        self.timeWidg.move(600,150)
        self.timeWidg.setStyleSheet(".QLabel{ color:white ; background-color:black ; font-size:60px }")

        self.dateWidg = DateWidget(self)
        self.dateWidg.move(250,5)
        self.dateWidg.setStyleSheet(".QLabel{ color:white ; background-color:black ; font-size:60px }")


class TimeWidget(QWidget):
    def __init__(self, parent=None):
        super(TimeWidget,self).__init__(parent)
        self.timeLabel = QLabel('Time',self)
        self.timeLabel.setAlignment(Qt.AlignCenter)
        self.setLayout = QVBoxLayout(self)
        self.layout().addWidget(self.timeLabel)
        
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayTimer)
        self.timer.start()
        QApplication.processEvents()
        self.setGeometry(40,40,400,120)


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

class DateWidget(QWidget):
    def __init__(self, parent=None):
        super(DateWidget,self).__init__(parent)
        self.dateLabel = QLabel('Date',self)
        self.dateLabel.setAlignment(Qt.AlignCenter)
        self.setLayout = QVBoxLayout(self)
        self.layout().addWidget(self.dateLabel)
        
        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.displayDate)
        self.timer.start()
        QApplication.processEvents()
        self.setGeometry(40,40,800,150)
        #self.setStyleSheet("background:black")

    def displayDate(self):
        print("connectedDate")
        datef =QDate.currentDate()
        print("middleDate")
        self.dateLabel.setText(datef.toString(Qt.DefaultLocaleLongDate))
        print("next")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow_V2()
    win.showFullScreen()
    sys.exit(app.exec_())
