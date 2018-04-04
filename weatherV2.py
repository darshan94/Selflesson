from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import (QApplication, QGridLayout, QGroupBox, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QLineEdit)

import pyowm


class WeatherWindow(QWidget):
    def __init__(self, parent=None):
        super(WeatherWindow,self).__init__(parent)

        self.weatherWidgetFinish_status = False
        grid = QGridLayout()
        
        self.label = QLabel("Weather")
        self.wStatus = QLabel("FALSE")
        grid.addWidget(self.label,0,0)
        grid.addWidget(self.wStatus,0,1)
        
        self.weatherObj = WeatherWorker()
        self.weatherThread = QThread()
        self.weatherObj.tempSignal.connect(self.updateTemp)
        self.weatherObj.weather_data_finished.connect(self._weatherFinished)
        self.weatherObj.moveToThread(self.weatherThread)
        self.weatherThread.started.connect(self.weatherObj.weatherFunction)
        

        QApplication.processEvents()
        self.setLayout(grid)
        self.resize(400,300)

    def startWeatherBackend(self):
        self.weatherThread.start()

    def updateTemp(self, temp):
        print("DEBUGGER POINT 2: SIGNAL RECEIVED")
        self.label.setText("Penang,Malaysia temperature:" + str(temp['temp']) + " \u00B0C")
        
    def _weatherFinished(self):
        print("FINISHED.START AGAIN")
        self.weatherThread.quit()
        self.weatherThread.wait()

        self.weatherWidgetFinish_status = True
        #self.wStatus.setText(str(self.weatherWidgetFinish_status))
        
    
class WeatherWorker(QObject):
    tempSignal = pyqtSignal(dict)
    weather_data_finished = pyqtSignal()
    
    def __init__(self, parent=None):
        super(WeatherWorker, self).__init__(parent)
        self.owm = pyowm.OWM('1589dbcc0e9608e5b70f0ede23e757c8') 

    def weatherFunction(self):
        print("DEBUGGER POINT 1: SIGNAL PROCESSING")
        observation = self.owm.weather_at_place('Penang,Malaysia')
        print("DEBUGGER POINT 2: SIGNAL PROCESSING")
        w = observation.get_weather()
        ctemp = w.get_temperature('celsius')
        self.tempSignal.emit(ctemp)
        
        self.weather_data_finished.emit()




if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    w = WeatherWindow()
    w.show()
    sys.exit(app.exec_())
