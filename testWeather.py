import sys
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt
 
import pywapi
 
class Main(QtGui.QMainWindow):
 
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.initUI()
 
    def initUI(self):
 
        self.line = QtGui.QLineEdit(self)
        self.line.move(90,35)
        self.line.resize(500,35)
        self.line.setStyleSheet("font-size:15px;")
 
        self.src = QtGui.QPushButton(QtGui.QIcon("icons/find.png"),"",self)
        self.src.move(600,34)
        self.src.resize(50,35)
        self.src.clicked.connect(self.Src)
        self.src.setShortcut("RETURN")
 
        self.pix = QtGui.QPixmap("")
 
        self.pic = QtGui.QLabel(self)
        self.pic.move(90,110)
        self.pic.resize(128,128)
        self.pic.setPixmap(self.pix)
 
        self.loc = QtGui.QLabel(self)
        self.loc.move(250,90)
        self.loc.resize(500,100)
        self.loc.setStyleSheet("font-size: 30px;")
 
        self.temp = QtGui.QLabel(self)
        self.temp.move(250,160)
        self.temp.resize(150,100)
        self.temp.setStyleSheet("font-size:50px;")
 
        self.hum = QtGui.QLabel(self)
        self.hum.move(410,160)
        self.hum.resize(250,100)
        self.hum.setStyleSheet("font-size:50px;")
 
        self.text = QtGui.QLabel(self)
        self.text.move(70,236)
        self.text.resize(180,50)
        self.text.setStyleSheet("font-size: 20px;")
        self.text.setAlignment(Qt.AlignCenter)
 
        self.time = QtGui.QLabel(self)
        self.time.move(250,211)
        self.time.resize(400,100)
        self.time.setStyleSheet("font-size: 20px;")
 
        self.error = QtGui.QLabel("No such place found ...",self)
        self.error.move(90,70)
        self.error.resize(500,200)
        self.error.setStyleSheet("font-size:40px;")
        self.error.hide()
 
        # 1
 
        self.first = QtGui.QLabel(self)
        self.first.move(100,300)
        self.first.resize(300,100)
        self.first.setStyleSheet("font-size:20px;")
 
        self.firstTemp = QtGui.QLabel(self)
        self.firstTemp.move(380,300)
        self.firstTemp.resize(150,100)
        self.firstTemp.setStyleSheet("font-size:20px;")
 
        self.firstHum = QtGui.QLabel(self)
        self.firstHum.move(460,300)
        self.firstHum.resize(150,100)
        self.firstHum.setStyleSheet("font-size:20px;")
 
        self.firstText = QtGui.QLabel(self)
        self.firstText.move(550,300)
        self.firstText.resize(200,100)
        self.firstText.setStyleSheet("font-size:20px;")
 
        # 2
 
        self.sec = QtGui.QLabel(self)
        self.sec.move(100,330)
        self.sec.resize(300,100)
        self.sec.setStyleSheet("font-size:20px;")
 
        self.secTemp = QtGui.QLabel(self)
        self.secTemp.move(380,330)
        self.secTemp.resize(150,100)
        self.secTemp.setStyleSheet("font-size:20px;")
 
        self.secHum = QtGui.QLabel(self)
        self.secHum.move(460,330)
        self.secHum.resize(150,100)
        self.secHum.setStyleSheet("font-size:20px;")
 
        self.secText = QtGui.QLabel(self)
        self.secText.move(550,330)
        self.secText.resize(200,100)
        self.secText.setStyleSheet("font-size:20px;")
 
        # 3
 
        self.three = QtGui.QLabel(self)
        self.three.move(100,360)
        self.three.resize(300,100)
        self.three.setStyleSheet("font-size:20px;")
 
        self.threeTemp = QtGui.QLabel(self)
        self.threeTemp.move(380,360)
        self.threeTemp.resize(150,100)
        self.threeTemp.setStyleSheet("font-size:20px;")
 
        self.threeHum = QtGui.QLabel(self)
        self.threeHum.move(460,360)
        self.threeHum.resize(150,100)
        self.threeHum.setStyleSheet("font-size:20px;")
 
        self.threeText = QtGui.QLabel(self)
        self.threeText.move(550,360)
        self.threeText.resize(200,100)
        self.threeText.setStyleSheet("font-size:20px;")
 
        # 4
 
        self.four = QtGui.QLabel(self)
        self.four.move(100,390)
        self.four.resize(300,100)
        self.four.setStyleSheet("font-size:20px;")
 
        self.fourTemp = QtGui.QLabel(self)
        self.fourTemp.move(380,390)
        self.fourTemp.resize(150,100)
        self.fourTemp.setStyleSheet("font-size:20px;")
 
        self.fourHum = QtGui.QLabel(self)
        self.fourHum.move(460,390)
        self.fourHum.resize(150,100)
        self.fourHum.setStyleSheet("font-size:20px;")
 
        self.fourText = QtGui.QLabel(self)
        self.fourText.move(550,390)
        self.fourText.resize(200,100)
        self.fourText.setStyleSheet("font-size:20px;")
 
        # 5
 
        self.five = QtGui.QLabel(self)
        self.five.move(100,420)
        self.five.resize(300,100)
        self.five.setStyleSheet("font-size:20px;")
 
        self.fiveTemp = QtGui.QLabel(self)
        self.fiveTemp.move(380,420)
        self.fiveTemp.resize(150,100)
        self.fiveTemp.setStyleSheet("font-size:20px;")
 
        self.fiveHum = QtGui.QLabel(self)
        self.fiveHum.move(460,420)
        self.fiveHum.resize(150,100)
        self.fiveHum.setStyleSheet("font-size:20px;")
 
        self.fiveText = QtGui.QLabel(self)
        self.fiveText.move(550,420)
        self.fiveText.resize(200,100)
        self.fiveText.setStyleSheet("font-size:20px;")
 
#---------Window settings --------------------------------
         
        self.setGeometry(300,300,750,500)
        self.setFixedSize(760,520)
        self.setWindowTitle("PySun")
        self.setWindowIcon(QtGui.QIcon("icons/partly.png"))
        self.setStyleSheet("background-color:")
        self.show()
 
    def Src(self):
        global text
        global temp
        global loc
        global time
        global hum
 
        global day1
        global day1Temp
        global day1Hum
        global day1Text
 
        global day2
        global day2Temp
        global day2Hum
        global day2Text
 
        global day3
        global day3Temp
        global day3Hum
        global day3Text
 
        global day4
        global day4Temp
        global day4Hum
        global day4Text
 
        global day5
        global day5Temp
        global day5Hum
        global day5Text
         
        try:
            text = self.line.text()
 
            location_info = pywapi.get_location_ids(text)
 
            for i in location_info:
                location_id = i
            for i in location_info.values():
                loc = i
 
            print(location_id,loc)
             
        except:
            self.text.hide()
            self.time.hide()
            self.pic.hide()
            self.temp.hide()
            self.loc.hide()
            self.hum.hide()
             
            self.error.show()
 
            self.first.hide()
            self.firstTemp.hide()
            self.firstHum.hide()
            self.firstText.hide()
 
            self.sec.hide()
            self.secTemp.hide()
            self.secHum.hide()
            self.secText.hide()
 
            self.three.hide()
            self.threeTemp.hide()
            self.threeHum.hide()
            self.threeText.hide()
 
            self.four.hide()
            self.fourTemp.hide()
            self.fourHum.hide()
            self.fourText.hide()
 
            self.five.hide()
            self.fiveTemp.hide()
            self.fiveHum.hide()
            self.fiveText.hide()
 
 
        weather_com_result = pywapi.get_weather_from_weather_com(location_id)
        print(weather_com_result['current_conditions']['text'],weather_com_result['current_conditions']['temperature']+"°",weather_com_result['current_conditions']['last_updated'],weather_com_result["current_conditions"]["humidity"])
         
        text = weather_com_result['current_conditions']['text']
        temp = weather_com_result['current_conditions']['temperature']+"°C"
        time = "last updated "+weather_com_result['current_conditions']['last_updated']
        hum = "☂ "+weather_com_result['current_conditions']['humidity']+"%"
 
         
        day1 = weather_com_result['forecasts'][0]['day_of_week'] + " " + weather_com_result['forecasts'][0]['date']
        day1Temp = weather_com_result['forecasts'][0]['high'] + "/" + weather_com_result['forecasts'][0]['low']
        day1Hum = "☂ "+weather_com_result['forecasts'][0]['day']['humidity']+"%"
        day1Text = weather_com_result['forecasts'][0]['day']['text']
 
        day2 = weather_com_result['forecasts'][1]['day_of_week'] + " " + weather_com_result['forecasts'][1]['date']
        day2Temp = weather_com_result['forecasts'][1]['high'] + "/" + weather_com_result['forecasts'][1]['low']
        day2Hum = "☂ "+weather_com_result['forecasts'][1]['day']['humidity']+"%"
        day2Text = weather_com_result['forecasts'][1]['day']['text']
 
        day3 = weather_com_result['forecasts'][2]['day_of_week'] + " " + weather_com_result['forecasts'][2]['date']
        day3Temp = weather_com_result['forecasts'][2]['high'] + "/" + weather_com_result['forecasts'][2]['low']
        day3Hum = "☂ "+weather_com_result['forecasts'][2]['day']['humidity']+"%"
        day3Text = weather_com_result['forecasts'][2]['day']['text']
 
        day4 = weather_com_result['forecasts'][3]['day_of_week'] + " " + weather_com_result['forecasts'][3]['date']
        day4Temp = weather_com_result['forecasts'][3]['high'] + "/" + weather_com_result['forecasts'][3]['low']
        day4Hum = "☂ "+weather_com_result['forecasts'][3]['day']['humidity']+"%"
        day4Text = weather_com_result['forecasts'][3]['day']['text']
 
        day5 = weather_com_result['forecasts'][4]['day_of_week'] + " " + weather_com_result['forecasts'][4]['date']
        day5Temp = weather_com_result['forecasts'][4]['high'] + "/" + weather_com_result['forecasts'][4]['low']
        day5Hum = "☂ "+weather_com_result['forecasts'][4]['day']['humidity']+"%"
        day5Text = weather_com_result['forecasts'][4]['day']['text']
 
        self.Forecast()
 
    def Forecast(self):
        global text
        global temp
        global loc
        global time
        global hum
 
        global day1
        global day1Temp
        global day1Hum
        global day1Text
 
        global day2
        global day2Temp
        global day2Hum
        global day2Text
 
        global day3
        global day3Temp
        global day3Hum
        global day3Text
 
        global day4
        global day4Temp
        global day4Hum
        global day4Text
 
        global day5
        global day5Temp
        global day5Hum
        global day5Text
 
        self.text.show()
        self.time.show()
        self.pic.show()
        self.temp.show()
        self.loc.show()
        self.hum.show()
 
        self.first.show()
        self.firstTemp.show()
        self.firstHum.show()
        self.firstText.show()
 
        self.sec.show()
        self.secTemp.show()
        self.secHum.show()
        self.secText.show()
 
        self.three.show()
        self.threeTemp.show()
        self.threeHum.show()
        self.threeText.show()
 
        self.four.show()
        self.fourTemp.show()
        self.fourHum.show()
        self.fourText.show()
 
        self.five.show()
        self.fiveTemp.show()
        self.fiveHum.show()
        self.fiveText.show()
         
        self.error.hide()
 
        self.loc.setText(loc)
        self.temp.setText(temp)
        self.text.setText(text)
        self.time.setText(time)
        self.hum.setText(hum)
 
        self.first.setText(day1)
        self.firstTemp.setText(day1Temp)
        self.firstHum.setText(day1Hum)
        self.firstText.setText(day1Text)
 
        self.sec.setText(day2)
        self.secTemp.setText(day2Temp)
        self.secHum.setText(day2Hum)
        self.secText.setText(day2Text)
 
        self.three.setText(day3)
        self.threeTemp.setText(day3Temp)
        self.threeHum.setText(day3Hum)
        self.threeText.setText(day3Text)
 
        self.four.setText(day4)
        self.fourTemp.setText(day4Temp)
        self.fourHum.setText(day4Hum)
        self.fourText.setText(day4Text)
 
        self.five.setText(day5)
        self.fiveTemp.setText(day5Temp)
        self.fiveHum.setText(day5Hum)
        self.fiveText.setText(day5Text)
 
        if text == "Partly Cloudy" or text == "Fair" or text == "AM Clouds / PM Sun":
            self.pix = QtGui.QPixmap("icons/partly.png")
            self.pic.setPixmap(self.pix)
             
        elif text == "Cloudy" or text == "Mostly Cloudy":
            self.pix = QtGui.QPixmap("icons/cloudy.png")
            self.pic.setPixmap(self.pix)
 
        elif text == "Sunny" or text == "Mostly Sunny":
            self.pix = QtGui.QPixmap("icons/sunny.png")
            self.pic.setPixmap(self.pix)
             
        elif text == "Showers Early" or text == "Showers" or text == "AM Showers" or text == "Few Showers" or text == "Scattered Showers" or text == "Light Rain Shower":
            self.pix = QtGui.QPixmap("icons/rainy.png")
            self.pic.setPixmap(self.pix)
 
        elif text == "Clear" or text == "Mostly Clear":
            self.pix = QtGui.QPixmap("icons/clear.png")
            self.pic.setPixmap(self.pix)
            self.pic.move(110,110)
 
        elif text == "Isolated T-Storms" or text == "PM T-Storms" or text == "Scattered T-Storms":
            self.pix = QtGui.QPixmap("icons/stormy.png")
            self.pic.setPixmap(self.pix)
     
         
def main():
    app = QtGui.QApplication(sys.argv)
    main= Main()
    main.show()
 
    sys.exit(app.exec_())
 
if __name__ == "__main__":
    main()
