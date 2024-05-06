from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import QIODevice
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


def close_com():

    serial.close()


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


def thres_changed():
    ui.thresHold.display(ui.thresSlider.value())
    # ui.imgTempOk.setPixmap(QtGui.QPixmap("img/greencircle.jpg"))
    # ui.imgTempOk.clear()


serial = QSerialPort()
serial.setBaudRate(115200)
update_list()

ui.openCom.clicked.connect(open_com)
ui.closeCom.clicked.connect(close_com)
ui.refrCom.clicked.connect(update_list)

ui.thresHold.display(ui.thresSlider.value())

ui.thresSlider.valueChanged.connect(thres_changed)

serial.readyRead.connect(com_ready_read)


ui.show()
app.exec()
