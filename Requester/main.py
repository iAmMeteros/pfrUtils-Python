import sys
import os
import resources
import time
import pymysql
import json
from pymysql.cursors import DictCursor
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QTableWidgetItem, QPushButton, QTableWidget, QInputDialog, QListWidgetItem

def openWindow(widgetClass):
    global mainWindow
    newWindow = widgetClass()
    newWindow.show()
    mainWindow.destroy()
    mainWindow = newWindow

def getFormattedUser(username):
    sqlconnection.commit()
    formatted = ""
    with sqlconnection.cursor() as cursor:
        query = f"""
            SELECT * FROM users WHERE username = "{username}"
        """
        cursor.execute(query)
        row = list(cursor)[0]
        formatted = f"{row['surname']} {row['name'][0]}. {row['patronymic'][0]}."
    return formatted

def formatSnils(snils):
    if len(snils) > 0:
        if not snils[-1].isnumeric():
            snils = snils[:-1]
        newsnils = ""
        snils = ''.join(snils.split('-'))
        for char in snils:
            newsnils += char
            if len(newsnils) == 4 or len(newsnils) == 8 or len(newsnils) == 12:
                newsnils = newsnils[:-1] + '-' + newsnils[-1]
        snils = newsnils
        if len(snils) > 14:
            snils = snils[:-1]
    return snils

class User():
    def __init__(self, username, surname, name, patronymic):
        self.username = username
        self.surname = surname
        self.name = name
        self.patronymic = patronymic


class MainMenu(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(path, 'mainmenu.ui'), self)

        self.pushButton.clicked.connect(lambda: openWindow(NewRequest))
        self.pushButton_2.clicked.connect(lambda: openWindow(MyRequests))

        self.label_3.setText(f"""
            <html><head/><body><p align="right"><span style=" font-size:16pt;">Вы: {user.surname} {user.name[0]}. {user.patronymic[0]}.</span></p></body></html>
        """)


class MyRequests(QWidget):
    requests = []

    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(path, 'myrequests.ui'), self)

        self.pushButton.clicked.connect(lambda: openWindow(MainMenu))
        self.pushButton_2.clicked.connect(self.update)
        self.listWidget.itemDoubleClicked.connect(self.clickHandle)

        self.update()

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.setInterval(1000)
        self.timer.start()

    def update(self):
        requests = []
        self.listWidget.clear()

        sqlconnection.commit()
        with sqlconnection.cursor() as cursor:
            query = f"""
                SELECT * FROM requests WHERE status IN (0, 1) AND personal = "{user.username}"
            """
            cursor.execute(query)
            for request in list(cursor):
                requests.append(request['id'])
                books = len(request['books'].split(';'))
                date = request['sendTime']
                if request['status'] == 0:
                    item = QListWidgetItem(f"Дел: {books} Отправлена {date} Статус: в очереди")
                elif request['status'] == 1:
                    item = QListWidgetItem(f"Дел: {books} Отправлена {date} Статус: выполняется")
                self.listWidget.addItem(item)
        self.requests = list(requests)
    
    def clickHandle(self, item):
        requestId = self.requests[self.listWidget.row(item)]
        sqlconnection.commit()
        with sqlconnection.cursor() as cursor:
            query = f"""
                SELECT * FROM requests WHERE id = "{requestId}"
            """
            cursor.execute(query)
            details = list(cursor)[0]
            self.detailsWindow = RequestDetails(details)
            self.detailsWindow.setWindowModality(QtCore.Qt.ApplicationModal)
            self.detailsWindow.show()


class RequestDetails(QWidget):
    data = dict()

    def __init__(self, details):
        super().__init__()
        uic.loadUi(os.path.join(path, 'requestDetails.ui'), self)
        self.pushButton.clicked.connect(self.close)

        self.lineEdit.setText(str(details['id']))
        self.lineEdit_2.setText(getFormattedUser(details['personal']))
        self.lineEdit_3.setText(str(details['sendTime']))
        self.textEdit.setText(details['comment'])
        if details['archivist'] != "":
            self.lineEdit_6.setText(getFormattedUser(details['archivist']))

        if str(details['receiveTime']) == '0000-00-00 00:00:00':
            self.lineEdit_4.setText('-')
        else:
            self.lineEdit_4.setText(str(details['receiveTime']))
        if details['status'] == 0:
            self.lineEdit_5.setText("В очереди")
        elif details['status'] == 1:
            self.lineEdit_5.setText("Исполняется")
        elif details['status'] == 2:
            self.lineEdit_5.setText("Выполнена")

        self.data = details
        books = details['books'].split(';')
        for book in books:
            sqlconnection.commit()
            with sqlconnection.cursor() as cursor:
                query = f"""
                    SELECT surname, name, patronymic FROM books
                    WHERE snils = "{book}"
                """
                cursor.execute(query)
                row = list(cursor)[0]
                item = QListWidgetItem(f"{book} - {row['surname']} {row['name'][0]}. {row['patronymic'][0]}.", self.listWidget)
                self.listWidget.addItem(item)

    def closeEvent(self, event):
        self.setWindowModality(QtCore.Qt.ApplicationModal)



class NewRequest(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(path, 'newrequest.ui'), self)

        self.pushButton.clicked.connect(lambda: openWindow(MainMenu))
        self.pushButton_3.clicked.connect(self.addBook)
        self.pushButton_2.clicked.connect(self.send)
        self.lineEdit.textEdited.connect(self.formatSnils)
        self.listWidget.itemDoubleClicked.connect(self.clickHandle)

        self.books = []

    def addBook(self):
        snils = self.lineEdit.text()

        if len(snils) < 14:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка")
            msg.setInformativeText('СНИЛС должен содержать 11 цифр!')
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            return
        if snils in self.books:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка")
            msg.setInformativeText('Дело уже в заявке.')
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            return

        sqlconnection.commit()
        with sqlconnection.cursor() as cursor:
            query = f"""
                SELECT * FROM books WHERE snils = "{snils}"
            """
            cursor.execute(query)
            row = list(cursor)
            if(len(row)) == 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Ошибка")
                msg.setInformativeText('Такого дела нет в базе.')
                msg.setWindowTitle("Ошибка")
                msg.exec_()
                return
            row = row[0]
            if str(row['in_request']) == "1":
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Ошибка")
                msg.setInformativeText('Дело уже запрошено.')
                msg.setWindowTitle("Ошибка")
                msg.exec_()
                return
            if str(row['in_archive']) == "0":
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Ошибка")
                msg.setInformativeText('Дело не в архиве.')
                msg.setWindowTitle("Ошибка")
                msg.exec_()
                return  
            book = QListWidgetItem(f"{snils} - {row['surname']} {row['name'][0]}. {row['patronymic'][0]}.", self.listWidget)
            self.lineEdit.setText('')
            self.listWidget.addItem(book)
            self.books.append(snils)

    def clickHandle(self, item):
        message = QMessageBox()
        res = message.question(self, '', "Убрать дело?", message.Yes | message.No)
        if res == message.Yes:
            self.listWidget.takeItem(self.listWidget.row(item))

    def send(self):
        commentary, ok = QInputDialog.getText(self, 'Отправка заявки', 'Оставьте свой комментарий (опционально)')
        if not ok:
            return
        for i in range(self.listWidget.count()):
            snils = self.listWidget.item(i).text()[:14]
            sqlconnection.commit()
            with sqlconnection.cursor() as cursor:
                query = f"""
                SELECT * FROM books WHERE snils = "{snils}"
                """
                cursor.execute(query)
                row = list(cursor)
                if(len(row)) == 0:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Ошибка")
                    msg.setInformativeText(f'Дело {snils} было удалено.')
                    msg.setWindowTitle("Ошибка")
                    msg.exec_()
                    continue
                row = row[0]
                if str(row['in_request']) == "1":
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Ошибка")
                    msg.setInformativeText(f'Дело {snils} уже запрошено.')
                    msg.setWindowTitle("Ошибка")
                    msg.exec_()
                    continue
                if str(row['in_archive']) == "0":
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Ошибка")
                    msg.setInformativeText(f'Дело {snils} не в архиве.')
                    msg.setWindowTitle("Ошибка")
                    msg.exec_()
                    continue

            with sqlconnection.cursor() as cursor:
                query = f"""
                    UPDATE books
                    SET in_request = 1
                    WHERE snils = "{snils}"
                """
                cursor.execute(query)
        snilsString = ";".join(self.books)
        print(snilsString)
        sendTime = time.strftime('%Y-%m-%d %H:%M:%S')

        with sqlconnection.cursor() as cursor:
            query = f"""
                INSERT INTO `requests`(`personal`, `books`, `sendTime`, `comment`) VALUES ("{user.username}", "{snilsString}", "{sendTime}", "{commentary}")
            """
            cursor.execute(query)
            sqlconnection.commit()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Операция выполнена!")
            msg.setInformativeText('Заявка отправлена.')
            msg.setWindowTitle("Статус")
            msg.exec_()
            openWindow(MainMenu)

    def formatSnils(self, snils):
        newsnils = formatSnils(snils)
        self.lineEdit.setText(newsnils)


if __name__ == '__main__':
    path = os.path.dirname(__file__)
    app = QApplication(sys.argv)
    userfile = open(os.path.join(path, "user.pfr"), "r")
    dbconfig = open(os.path.join(path, "dbconfig.pfr"), "r")
    username = userfile.read()
    dbconfigdict = json.loads(dbconfig.read())
    try:
        sqlconnection = pymysql.connect(
            host = dbconfigdict['host'],
            user = dbconfigdict['user'],
            password = dbconfigdict['password'],
            db = dbconfigdict['db'],
            charset = 'utf8mb4',
            cursorclass = DictCursor
        )
    except:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText("Ошибка")
        msg.setInformativeText('Не удается подключиться к серверу.')
        msg.setWindowTitle("Ошибка")
        sys.exit(msg.exec_())
    user = None
    with sqlconnection.cursor() as cursor:
        query = f"""
            SELECT * FROM users WHERE username = "{username}"
        """
        cursor.execute(query)
        row = list(cursor)[0]
        user = User(username, row['surname'], row['name'], row['patronymic'])
    mainWindow = MainMenu()
    mainWindow.show()
    sys.exit(app.exec_())