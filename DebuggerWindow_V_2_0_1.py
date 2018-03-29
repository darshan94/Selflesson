from PyQt5.QtCore import (Qt,QThread,pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import (QApplication, QGridLayout, QGroupBox, QVBoxLayout,QHBoxLayout, QWidget, QLabel, QLineEdit)
import sys
import time


class TestSignal(QThread):

    progress = pyqtSignal(int)
    receiver = pyqtSignal(int)
    
    def __init__(self):
        super(TestSignal,self).__init__()
        printValue = 'Number'

    def __del__(self):
        self.wait()

    def run(self):
        for i in range(100):
            self.progress.emit(i)
            time.sleep(1)

    def printmy(self,value):
        self.printValue == value
        print("RECEIVE: " +str(self.printValue))
        

class MainWindow(QWidget):

    
    def __init__(self, parent=None):
        super(MainWindow,self).__init__(parent)
        
        grid = QGridLayout()

        self.groupBox=QGroupBox("FACE NAVIGATION")
        self.mouth_Open_Counter = QLabel("MOUTH OPEN COUNTER : ")
        self.mouth_Closed_Counter = QLabel("MOUTH CLOSE COUNTER: ")
        self.mouth_condition = QLabel("MOUTH CONDITION : ")

        self.leftEyeOpen = QLabel("LEFT EYE OPEN COUNTER : ")
        self.leftEyeClose = QLabel("LEFT EYE CLOSE COUNTER: ")
        self.rightEyeOpen = QLabel("RIGHT EYE OPEN COUNTER : ")
        self.rightEyeClose = QLabel("RIGHT EYE CLOSE COUNTER: ")
        self.leftEyeCondition= QLabel("LEFT EYE CONDITION: ")
        self.rightEyeCondition = QLabel("RIGHT EYE CONDITION: ")
        
        self.activateWindow = QLabel("ACTIVATED FRAME : ")    
        
        self.mouth_Open_Counter_Value = QLabel()
        self.mouth_Closed_Counter_Value = QLabel()
        self.mouth_condition_Value = QLabel()
        self.leftEyeOpenValue = QLabel("#")
        self.leftEyeCloseValue = QLabel("#")
        self.rightEyeOpenValue = QLabel("#")
        self.rightEyeCloseValue = QLabel("#")
        self.leftEyeConditionValue= QLabel("#")
        self.rightEyeConditionValue = QLabel("#")
        
        self.activateWindowValue = QLabel("MAIN")

        #self.thread = Navigation()
        self.mouth_Open_Counter_Value.setText("#")
        self.mouth_Closed_Counter_Value.setText("#")
        self.mouth_condition_Value.setText("#")

        self.groupBox.setStyleSheet("color: white ;font: bold 12px")

        self.thread = TestSignal()
        self.thread.progress.connect(self.updateMODate)
   
        self.thread.start()
        #self.thread.Mouth_Open_progress.connect(self.updateMODate)
        #self.thread.Mouth_Close_progress.connect(self.updateMCDate)
        #self.thread.Mouth_State_progress.connect(self.updateMSDate)
        #self.thread.start()
        
        QApplication.processEvents()
        verticalLayout = QVBoxLayout()
        horizontalLayout = QHBoxLayout()
        horizontalLayout1 = QHBoxLayout()
        horizontalLayout2 = QHBoxLayout()
        horizontalLayout3 = QHBoxLayout()
        horizontalLayout4 = QHBoxLayout()
        horizontalLayout5 = QHBoxLayout()
        horizontalLayout6 = QHBoxLayout()
        horizontalLayout7 = QHBoxLayout()
        horizontalLayout8 = QHBoxLayout()
        horizontalLayout9 = QHBoxLayout()

        horizontalLayout.addWidget(self.mouth_Open_Counter)
        horizontalLayout.addWidget(self.mouth_Open_Counter_Value)
        horizontalLayout1.addWidget(self.mouth_Closed_Counter)
        horizontalLayout1.addWidget(self.mouth_Closed_Counter_Value)
        horizontalLayout2.addWidget(self.mouth_condition)
        horizontalLayout2.addWidget(self.mouth_condition_Value)
        horizontalLayout3.addWidget(self.leftEyeOpen)
        horizontalLayout3.addWidget(self.leftEyeOpenValue)
        horizontalLayout4.addWidget(self.leftEyeClose)
        horizontalLayout4.addWidget(self.leftEyeCloseValue)
        horizontalLayout5.addWidget(self.rightEyeOpen)
        horizontalLayout5.addWidget(self.rightEyeOpenValue)
        horizontalLayout6.addWidget(self.rightEyeClose)
        horizontalLayout6.addWidget(self.rightEyeCloseValue)
        horizontalLayout7.addWidget(self.leftEyeCondition)
        horizontalLayout7.addWidget(self.leftEyeConditionValue)
        horizontalLayout8.addWidget(self.rightEyeCondition)
        horizontalLayout8.addWidget(self.rightEyeConditionValue)
        horizontalLayout9.addWidget(self.activateWindow)
        horizontalLayout9.addWidget(self.activateWindowValue)
        
        verticalLayout.addLayout(horizontalLayout)
        verticalLayout.addLayout(horizontalLayout1)
        verticalLayout.addLayout(horizontalLayout2)
        verticalLayout.addLayout(horizontalLayout3)
        verticalLayout.addLayout(horizontalLayout4)
        verticalLayout.addLayout(horizontalLayout5)
        verticalLayout.addLayout(horizontalLayout6)
        verticalLayout.addLayout(horizontalLayout7)
        verticalLayout.addLayout(horizontalLayout8)
        verticalLayout.addLayout(horizontalLayout9)
        
   
        verticalLayout.addStretch(1)
        self.groupBox.setLayout(verticalLayout)
        
        grid.addWidget(self.groupBox,0,0)

        QApplication.processEvents()
        self.setLayout(grid)
        self.setWindowTitle("EXPRESSION DATA")
        self.resize(400,300)
        self.setStyleSheet("background-color : black ; font :white")

    @pyqtSlot(int)
    def updateMODate(self,value):
        print(str(value))
        self.mouth_Open_Counter_Value.setText(str(value))
        if value == 23:
            print("SEND NUMBER")
            self.receiver.emit(value)

    def updateMCDate(self,value):
        print(str(value))
        self.mouth_Closed_Counter_Value.setText(str(value))

    def updateMSDate(self,value):
        print(value)
        self.mouth_condition_Value.setText(value)
        

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    analysisWin = MainWindow()
    analysisWin.show()
    #analysisWin.showFullScreen()
    sys.exit(app.exec_())
