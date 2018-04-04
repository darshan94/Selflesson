from PyQt5.QtCore import QDate, QTime, QDateTime, Qt,QTimer, pyqtSlot, pyqtSignal, QObject, QThread
from PyQt5.QtWidgets import QGridLayout,QDockWidget,QApplication,QWidget,QLabel, QVBoxLayout, QMainWindow, QGroupBox, QVBoxLayout, QHBoxLayout


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
    import sys
    app = QApplication(sys.argv)
    win_sts = DateWidget()
    win_sts.show()
    sys.exit(app.exec_())
