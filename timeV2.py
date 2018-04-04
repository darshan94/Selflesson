from PyQt5.QtCore import QDate, QTime, QDateTime, Qt,QTimer, pyqtSlot, pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QGridLayout,QDockWidget,QApplication,QWidget,QLabel, QVBoxLayout, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout

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

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win_sts = TimeWidget()
    win_sts.show()
    sys.exit(app.exec_())
