from weatherV2 import WeatherWindow
from timeV2 import TimeWidget
from emailV2 import emailWidget
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QStackedWidget,QListWidget,QApplication, QGridLayout, QGroupBox, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QLineEdit)

class Module_Stack(QWidget):
    def __init__(self):
        super(Module_Stack, self).__init__()
        print("[INFO-MODULE-STACK] : INITILIATION STARTED")
        
        self.leftlists = QListWidget()
        self.leftlists.insertItem(0,'Email')
        self.leftlists.insertItem(1,'Weather')

        print("[INFO-MODULE-STACK] : QLISTWIDGET IS CREATED")

        self.stack1 = emailWidget()

        print("[INFO-MODULE-STACK] : EMAIL WIDGET OBJECT IS CREATED")
        #self.stack2 = WeatherWindow()

        self.Stack = QStackedWidget(self)
        #self.Stack.addWidget(self.stack1)
        #self.Stack.addWidget(self.stack2)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.leftlists)
        #hbox.addWidget(self.Stack)

        self.setLayout(hbox)
        #self.leftlists.currentRowChanged.connect(self.display)
        

    def display(self):
        self.Stack.setCurrentIndex(i)
        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = Module_Stack()
    w.show()
    sys.exit(app.exec_())
