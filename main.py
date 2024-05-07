from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice
import configparser
# from pyqtgraph import PlotWidget
# import pyqtgraph as pg
# import sys

app = QtWidgets.QApplication([])
ui = uic.loadUi("main.ui")
ui.setWindowTitle("Датчик температуры на шумовом диоде")


def update_list():
    port_list = []
    ports = QSerialPortInfo().availablePorts()
    for port in ports:
        port_list.append(port.portName())
    ui.comList.clear()
    ui.comList.addItems(port_list)



def open_com():
    serial.setPortName(ui.comList.currentText())
    serial.open(QIODevice.ReadWrite)
    serial.clear()

    if serial.isOpen():
        # serial.clear()
        tx = ':r\r\n'
        serial.write(tx.encode())
        ui.openCom.setEnabled(False)
        ui.closeCom.setEnabled(True)


def close_com():

    serial.close()
    ui.openCom.setEnabled(True)
    ui.closeCom.setEnabled(False)


listX1 = []
listX2 = []
for x in range(100):
    listX1.append(float(x))
    listX2.append(float(x))

listY1 = []
listY2 = []
for y in range(100):
    listY1.append(0)
    listY2.append(0)


def com_ready_read():
    rx = serial.readLine()
    rxs = str(rx, 'utf-8').strip()
    data = rxs.split(',')
    print(data)
    ui.VDC.display(data[0])
    ui.Curr.display(data[1])

    global listX1
    global listX2
    global listY1
    global listY2
    global slope
    global intercept

    # intdata1 = round(float(data[1]))
    # intdata2 = round(float(data[2]))

    listY1 = listY1[1:]
    listY1.append(float(data[1]))
    ui.currGraph.clear()

    listY2 = listY2[1:]
    # listY2.append(intdata2)
    listY2.append(float(data[2]))
    ui.pulseGraph.clear()

    ui.currGraph.plot(listX1, listY1)
    ui.pulseGraph.plot(listX2, listY2)

    threshold = round((float(data[0])-intercept)/slope)
    if -50 <= threshold <= 150:
        ui.thresHold.display(threshold)
    else:
        ui.thresHold.display('Err')

    current = float(data[1])
    if current < 0.08:
        ui.imgTempLow.clear()
        ui.imgTempOk.clear()
        ui.imgTempHigh.setPixmap(QtGui.QPixmap("img/redcircle.jpg"))
    elif 0.08 <= current <= 0.12:
        ui.imgTempLow.clear()
        ui.imgTempOk.setPixmap(QtGui.QPixmap("img/greencircle.jpg"))
        ui.imgTempHigh.clear()
    else:
        ui.imgTempLow.setPixmap(QtGui.QPixmap("img/bluecircle.jpg"))
        ui.imgTempOk.clear()
        ui.imgTempHigh.clear()




def thres_changed():
    ui.thresHold.display(ui.thresSlider.value())
    # ui.imgTempOk.setPixmap(QtGui.QPixmap("img/greencircle.jpg"))
    # ui.imgTempOk.clear()

slope = 1
intercept = 1

def manual_calibrate():
    point1 = (float(ui.uX1.text()), float(ui.uY1.text()))
    point2 = (float(ui.uX2.text()), float(ui.uY2.text()))
    print(point1)
    print(point2)

    global slope
    global intercept

    slope = (point2[1] - point1[1]) / (point2[0] - point1[0])
    intercept = point1[1] - slope * point1[0]


    # Создаем массивы x и y
    x_values = [float(xC) for xC in range(-50, 151)]  # x от -50 до 150
    y_values = [slope * x + intercept for x in x_values]

    print("Первые несколько значений x и y:")
    for x, y in zip(x_values[:5], y_values[:5]):
        print(f"x = {x}, y = {y}")

    ui.tempGraph.clear()

    ui.tempGraph.plot(x_values, y_values)

    ui.openCom.setEnabled(True)



def save_calibration_coordinates():
    point1 = (float(ui.uX1.text()), float(ui.uY1.text()))
    point2 = (float(ui.uX2.text()), float(ui.uY2.text()))
    config = configparser.ConfigParser()
    config['Coordinates'] = {
        'Point1_x': str(point1[0]),
        'Point1_y': str(point1[1]),
        'Point2_x': str(point2[0]),
        'Point2_y': str(point2[1])
    }
    with open('calibration.ini', 'w') as configfile:
        config.write(configfile)
    print("Координаты успешно сохранены в файл calibration.ini")

# Функция для чтения сохраненных координат из файла
def read_calibration_coordinates():
    config = configparser.ConfigParser()
    config.read('calibration.ini')
    point1_x = str(config['Coordinates']['Point1_x'])
    ui.uX1.setText(point1_x)
    point1_y = str(config['Coordinates']['Point1_y'])
    ui.uY1.setText(point1_y)
    point2_x = str(config['Coordinates']['Point2_x'])
    ui.uX2.setText(point2_x)
    point2_y = str(config['Coordinates']['Point2_y'])
    ui.uY2.setText(point2_y)
    manual_calibrate()
    ui.openCom.setEnabled(True)
    # return (point1_x, point1_y), (point2_x, point2_y)


serial = QSerialPort()
serial.setBaudRate(115200)
update_list()

ui.openCom.clicked.connect(open_com)
ui.closeCom.clicked.connect(close_com)
ui.refrCom.clicked.connect(update_list)

#ui.thresHold.display(ui.thresSlider.value())

#ui.thresSlider.valueChanged.connect(thres_changed)

ui.manualCalibrationButton.clicked.connect(manual_calibrate)
ui.saveCalibrationButton.clicked.connect(save_calibration_coordinates)
ui.loadCalibrationButton.clicked.connect(read_calibration_coordinates)

serial.readyRead.connect(com_ready_read)


ui.show()
app.exec()
