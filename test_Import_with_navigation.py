from weatherV2 import WeatherWindow
from timeV2 import TimeWidget
from emailV2 import emailWidget
from navigationV2 import Navigation

from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QStackedWidget,QListWidget,QApplication, QGridLayout, QGroupBox, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QLineEdit)

class Module_Stack(QWidget):
    def __init__(self):
        super(Module_Stack, self).__init__()

        self.navObj = Navigation()
        self.navThread = QThread()

        self.navObj.Pattern_progress.connect(self.moduleSelection)
        self.navObj.finished.connect(self.naviFinished)
        self.navObj.moveToThread(self.navThread)
        self.navThread.started.connect(self.navObj.navigationMode_1)
        
        self.emailStack = emailWidget(self)
        self.emailStack.hide()
        self.weatherStack = WeatherWindow(self)
        self.weatherStack.hide()
        #self.emailStack.startEmailBackend()
        self.setNaviMode("SubWin")
        self.startMainNav()

    def startMainNav(self):
        self.navThread.start()

    def naviFinished(self):
        self.navThread.quit()
        self.navThread.wait()

    def setNaviMode(self,_winType):
        self.navObj.setWindowType(_winType)

    def moduleSelection(self,value):
        if value == 'PATTERN_11':
            self.emailStack.show()
            self.emailStack.startEmailBackend()

        elif value == 'PATTERN_5':
            self.emailStack.show()
            self.weatherStack.startWeatherBackend()

        else:
            print("ERROR")
            
        
        
        
if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    w = Module_Stack()
    w.show()
    sys.exit(app.exec_())
