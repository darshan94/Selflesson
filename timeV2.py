from PyQt5.QtCore import QDate, QTime, QDateTime, Qt,QTimer, pyqtSlot, pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QGridLayout,QDockWidget,QApplication,QWidget,QLabel, QVBoxLayout, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout


class TimeWorker(QObject):
    min_Signal = pyqtSignal(str)
    sec_Signal = pyqtSignal(str)
    hr_signal = pyqtSignal(str)
    stringForm_Signal = pyqtSignal(str)

    def __init__(self, parent=None):
        super(TimeWorker,self).__init__(parent)
        self.stringForm = "00000"

    def displayTimer(self):
        print("connected")
        self.timef =QTime.currentTime()
        print("middle")
        self.stringForm = self.timef.toString(Qt.ISODate)
        self.stringForm_Signal.emit(self.stringForm)
        #minuteTime = timef.minute()
        #hourTime = timef.hour()
        #secTime = timef.second()
        #print(str(hourTime)+" : "+str(minuteTime))
        #print("next")

class TimeWidget(QWidget):
    def __init__(self, parent=None):
        super(TimeWidget,self).__init__(parent)
        self.timeLabel = QLabel('Time',self)
        self.timeLabel.setAlignment(Qt.AlignCenter)
        self.setLayout = QVBoxLayout(self)
        self.layout().addWidget(self.timeLabel)


        self.worker = TimeWorker(self)
        self.timeThread = QThread(self)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)

        self.timer.moveToThread(self.timeThread)
        self.worker.moveToThread(self.timeThread)
        
        self.timer.timeout.connect(self.worker.displayTimer)
        self.worker.stringForm_Signal.connect(self.updateTime)
        self.timeThread.started.connect(self.timer.start)
        self.timeThread.start()
        QApplication.processEvents()
        self.setGeometry(40,40,400,120)

    def updateTime(self,value):
        self.timeLabel.setText(value) 

    

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win_sts = TimeWidget()
    win_sts.show()
    sys.exit(app.exec_())






 

    
