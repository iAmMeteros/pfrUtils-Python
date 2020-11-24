from PyQt5 import QtCore, QtGui, QtWidgets
import sys, os, json, ctypes


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


class MainWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        folder = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if folder == "":
            sys.exit()
        else:
            self.path = folder

            try:
                dbconfig = open(os.path.join(folder, "dbconfig.pfr"), 'r')
                userfile = open(os.path.join(folder, "user.pfr"), "r")
            except:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Critical)
                msg.setText("Ошибка")
                msg.setInformativeText('Файлы конфигурации не найдены.')
                msg.setWindowTitle("Ошибка")
                msg.exec_()
                sys.exit()
            dbconfigdict = json.loads(dbconfig.read())

            self.host = dbconfigdict['host']
            self.user = dbconfigdict['user']
            self.password = dbconfigdict['password']
            self.db = dbconfigdict['db']
            self.username = userfile.read()

            self.setupUi()

            self.lineEdit_6.setText(self.username)
            self.lineEdit_7.setText(self.host)
            self.lineEdit_8.setText(self.user)
            self.lineEdit_9.setText(self.password)
            self.lineEdit_10.setText(self.db)

            self.pushButton.clicked.connect(self.save)

            dbconfig.close()
            userfile.close()

    def save(self):
        if len(self.lineEdit_6.text()) * len(self.lineEdit_7.text()) * len(self.lineEdit_8.text()) * len(self.lineEdit_9.text()) * self.lineEdit_10.text() == 0:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Ошибка")
            msg.setInformativeText('Заполните все поля!')
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            return
        dbconfig = open(os.path.join(self.path, "dbconfig.pfr"), 'w')
        userfile = open(os.path.join(self.path, "user.pfr"), "w")
        dbconfig.write(json.dumps({
            "host": self.lineEdit_7.text(),
            "user": self.lineEdit_8.text(),
            "password": self.lineEdit_9.text(),
            "db": self.lineEdit_10.text()
        }))
        userfile.write(self.lineEdit_6.text())
        dbconfig.close()
        userfile.close()

    def setupUi(self):
        Form = self
        Form.setObjectName("Конфигуратор")
        Form.resize(281, 391)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(10, 10, 189, 35))
        self.label.setObjectName("label")
        self.lineEdit_6 = QtWidgets.QLineEdit(Form)
        self.lineEdit_6.setGeometry(QtCore.QRect(10, 70, 261, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_6.setFont(font)
        self.lineEdit_6.setText("")
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.label_10 = QtWidgets.QLabel(Form)
        self.label_10.setGeometry(QtCore.QRect(10, 50, 211, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.lineEdit_7 = QtWidgets.QLineEdit(Form)
        self.lineEdit_7.setGeometry(QtCore.QRect(10, 130, 261, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_7.setFont(font)
        self.lineEdit_7.setText("")
        self.lineEdit_7.setObjectName("lineEdit_7")
        self.label_11 = QtWidgets.QLabel(Form)
        self.label_11.setGeometry(QtCore.QRect(10, 110, 211, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(Form)
        self.label_12.setGeometry(QtCore.QRect(10, 170, 211, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.lineEdit_8 = QtWidgets.QLineEdit(Form)
        self.lineEdit_8.setGeometry(QtCore.QRect(10, 190, 261, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_8.setFont(font)
        self.lineEdit_8.setText("")
        self.lineEdit_8.setObjectName("lineEdit_8")
        self.label_13 = QtWidgets.QLabel(Form)
        self.label_13.setGeometry(QtCore.QRect(10, 230, 211, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.lineEdit_9 = QtWidgets.QLineEdit(Form)
        self.lineEdit_9.setGeometry(QtCore.QRect(10, 250, 261, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_9.setFont(font)
        self.lineEdit_9.setText("")
        self.lineEdit_9.setObjectName("lineEdit_9")
        self.label_14 = QtWidgets.QLabel(Form)
        self.label_14.setGeometry(QtCore.QRect(10, 290, 211, 18))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.lineEdit_10 = QtWidgets.QLineEdit(Form)
        self.lineEdit_10.setGeometry(QtCore.QRect(10, 310, 261, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.lineEdit_10.setFont(font)
        self.lineEdit_10.setText("")
        self.lineEdit_10.setObjectName("lineEdit_10")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(10, 350, 261, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label.setText(_translate("Form", "<html><head/><body><p><span style=\" font-size:22pt;\">Конфигуратор</span></p></body></html>"))
        self.label_10.setText(_translate("Form", "Имя пользователя"))
        self.label_11.setText(_translate("Form", "Хост MySQL"))
        self.label_12.setText(_translate("Form", "Имя пользователя MySQL"))
        self.label_13.setText(_translate("Form", "Пароль MySQL"))
        self.label_14.setText(_translate("Form", "Имя БД"))
        self.pushButton.setText(_translate("Form", "Сохранить"))
    

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    if (not is_admin()):
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()
    mainWindow = MainWidget()
    mainWindow.show()
    sys.exit(app.exec_())