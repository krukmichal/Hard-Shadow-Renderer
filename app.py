from PyQt6 import QtWidgets, QtGui
import sys
from pathlib import Path
import shadow_mapping
import config

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My PyQt6 App")
        self.setGeometry(700, 400, 400, 600)

        button1 = QtWidgets.QPushButton("Browse obj file", self)
        button1.clicked.connect(lambda: self.showDialog(self.lineEdit1))
        button1.move(50, 50)
        button1.setFixedWidth(300)

        self.lineEdit1 = QtWidgets.QLineEdit(config.object_filename, self)
        self.lineEdit1.setReadOnly(True)
        self.lineEdit1.move(50,100)
        self.lineEdit1.setFixedWidth(300)

        button2 = QtWidgets.QPushButton("Browse skybox file", self)
        button2.clicked.connect(lambda: self.showDialog(self.lineEdit2))
        button2.move(50, 150)
        button2.setFixedWidth(300)

        self.lineEdit2 = QtWidgets.QLineEdit("default", self)
        self.lineEdit2.setReadOnly(True)
        self.lineEdit2.move(50,200)
        self.lineEdit2.setFixedWidth(300)

        self.checkbox1 = QtWidgets.QCheckBox("shadowmap", self)
        self.checkbox1.setChecked(True)
        self.checkbox1.move(50,250)

        self.checkbox2 = QtWidgets.QCheckBox("Add bias", self)
        self.checkbox2.setChecked(True)
        self.checkbox2.move(50,300)

        self.checkbox3 = QtWidgets.QCheckBox("Poisson", self)
        self.checkbox3.setChecked(True)
        self.checkbox3.move(50,350)

#        self.lineEdit3 = QtWidgets.QLineEdit("4", self)
#        self.lineEdit3.setReadOnly(False)
#        self.lineEdit3.move(50,400)
#        self.lineEdit3.setFixedWidth(300)

        button3 = QtWidgets.QPushButton("Run", self)
        button3.move(50, 400)
        button3.clicked.connect(self.run)
        button3.setFixedWidth(300)

        self.show()

    def showDialog(self, lineEdit):
        home_dir = str("~/studia/trak/p3")
        fname = QtWidgets.QFileDialog.getOpenFileName(self,'give me some obj file', home_dir)
        if fname[0]:
            lineEdit.setText(fname[0])
    
    def run(self):
        config.if_bias = self.checkbox2.isChecked()
        config.if_shadow_map = self.checkbox1.isChecked()
        config.ifpoissonDisk = self.checkbox3.isChecked()
#        config.numberofsamples = int(self.lineEdit3.text())
        shadow_mapping.start(self.lineEdit1.text(), self.lineEdit2.text())

app = QtWidgets.QApplication([])
window = MainWindow()
app.exec()
