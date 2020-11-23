import sys
import os
import resources
import time
import pymysql
import json
from pymysql.cursors import DictCursor
from PyQt5 import uic, QtCore, QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QListWidgetItem, QMessageBox, QTableWidgetItem, QPushButton, QTableWidget, QInputDialog

def openWindow(widgetClass):
    global mainWindow
    newWindow = widgetClass()
    newWindow.show()
    mainWindow.destroy()
    mainWindow = newWindow

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

        self.pushButton.clicked.connect(lambda: openWindow(BookBase))
        self.pushButton_2.clicked.connect(lambda: openWindow(InboxRequests))
        self.pushButton_3.clicked.connect(lambda: openWindow(AllRequests))
        self.pushButton_4.clicked.connect(lambda: openWindow(MyRequests))

        self.label_3.setText(f"""
            <html><head/><body><p align="right"><span style=" font-size:16pt;">Вы: {user.surname} {user.name[0]}. {user.patronymic[0]}.</span></p></body></html>
        """)


class BookBase(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(path, 'base.ui'), self)

        self.pushButton.clicked.connect(lambda: openWindow(MainMenu))
        self.pushButton_2.clicked.connect(self.updateTable)
        self.pushButton_3.clicked.connect(self.showRegisterWidget)
        self.pushButton_4.clicked.connect(self.showFiltersWindow)

        self.filters = ""
        self.dictFilters = {
            'surname': '',
            'name': '',
            'patronymic': '',
            'snils': '',
            'status': 0
        }

        self.updateTable()

    def showFiltersWindow(self):
        self.newWidget = BaseFilters(self)
        self.newWidget.setWindowModality(QtCore.Qt.ApplicationModal)
        self.newWidget.show()

    def showRegisterWidget(self):
        self.newWidget = AddBook()
        self.newWidget.setWindowModality(QtCore.Qt.ApplicationModal)
        self.newWidget.show()

    def updateTable(self):
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setHorizontalHeaderLabels(['СНИЛС', 'Фамилия', 'Имя', 'Отчество', 'Статус'])
        self.tableWidget.setEditTriggers(QTableWidget.NoEditTriggers)

        sqlconnection.commit()
        with sqlconnection.cursor() as cursor:
            if self.filters == "":
                query = """SELECT * FROM books"""
            else:
                query = f"""
                    SELECT * FROM books
                    WHERE {self.filters}
                """
            cursor.execute(query)
            for i, row in enumerate(list(cursor)):
                self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(row['snils'])))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(str(row['surname'])))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(str(row['name'])))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(str(row['patronymic'])))
                if row['in_archive'] == 1:
                    if row['in_request'] == 1:
                        status_item = QTableWidgetItem('В архиве, запрошено')
                        self.tableWidget.setItem(i, 4, status_item)
                    else:
                        status_item = QTableWidgetItem('В архиве')
                        self.tableWidget.setItem(i, 4, status_item)
                else:
                    status_item = QTableWidgetItem('У сотрудника')
                    self.tableWidget.setItem(i, 4, status_item)

        self.tableWidget.resizeColumnToContents(0)
        self.tableWidget.resizeColumnToContents(1)
        self.tableWidget.resizeColumnToContents(2)
        self.tableWidget.resizeColumnToContents(3)
        self.tableWidget.resizeColumnToContents(4)
        self.tableWidget.itemDoubleClicked.connect(self.clickHandle)

    def clickHandle(self, cell):
        snils = self.tableWidget.item(cell.row(), 0).text()
        self.editor = EditBook(snils)
        self.editor.setWindowModality(QtCore.Qt.ApplicationModal)
        self.editor.show()


class BaseFilters(QWidget):
    def __init__(self, parent):
        super().__init__()
        uic.loadUi(os.path.join(path, 'filters.ui'), self)
        self.pushButton_4.clicked.connect(self.close)
        self.pushButton_5.clicked.connect(self.apply)
        self.pushButton_6.clicked.connect(self.clear)
        self.lineEdit.textEdited.connect(self.formatSnils)

        self.parent = parent

        self.lineEdit.setText(parent.dictFilters['snils'])
        self.lineEdit_2.setText(parent.dictFilters['surname'])
        self.lineEdit_3.setText(parent.dictFilters['name'])
        self.lineEdit_4.setText(parent.dictFilters['patronymic'])
        self.comboBox.setCurrentIndex(parent.dictFilters['status'])

    def formatSnils(self, snils):
        newsnils = formatSnils(snils)
        self.lineEdit.setText(newsnils)

    def apply(self):
        snils = self.lineEdit.text()
        surname = self.lineEdit_2.text()
        name = self.lineEdit_3.text()
        patronymic = self.lineEdit_4.text()
        status = self.comboBox.currentIndex()

        if status == 0:
            statusStr = ""
        elif status == 1:
            statusStr = "AND in_archive = 1"
        elif status == 2:
            statusStr = "AND in_request = 1"

        newFilters = f"""
            snils LIKE "{snils}%" AND
            surname LIKE "%{surname}%" AND
            name LIKE "%{name}%" AND
            patronymic LIKE "%{patronymic}%" {statusStr}
        """

        self.parent.filters = newFilters
        self.parent.dictFilters = {
            'surname': surname,
            'name': name,
            'patronymic': patronymic,
            'snils': snils,
            'status': status
        }
        self.parent.updateTable()
        self.close()

    def clear(self):
        self.parent.filters = ""
        self.parent.dictFilters = {
            'surname': '',
            'name': '',
            'patronymic': '',
            'snils': '',
            'status': 0
        }
        self.parent.updateTable()
        self.close()
        
    def closeEvent(self, event):
        self.setWindowModality(QtCore.Qt.ApplicationModal)

class AddBook(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(os.path.join(path, 'addBook.ui'), self)

        self.pushButton.clicked.connect(self.registerBook)
        self.pushButton_2.clicked.connect(self.close)
        self.lineEdit.textEdited.connect(self.formatSnils)

    def formatSnils(self, snils):
        newsnils = formatSnils(snils)
        self.lineEdit.setText(newsnils)

    def registerBook(self):
        snils = self.lineEdit.text()
        surname = self.lineEdit_2.text()
        name = self.lineEdit_3.text()
        patronymic = self.lineEdit_4.text()

        if len(snils) * len(surname) * len(name) * len(patronymic) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка")
            msg.setInformativeText('Заполните все поля!')
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            return
        if len(snils) != 14:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка")
            msg.setInformativeText('СНИЛС должен содержать 11 цифр!')
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            return

        sqlconnection.commit()
        with sqlconnection.cursor() as cursor:
            query = f"""
            SELECT snils FROM books WHERE snils = "{snils}"
            """
            cursor.execute(query)
            if len(list(cursor)) > 0:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Ошибка")
                msg.setInformativeText('Дело с таким СНИЛС уже существует.')
                msg.setWindowTitle("Ошибка")
                msg.exec_()
                return
        sqlconnection.commit()

        with sqlconnection.cursor() as cursor:
            query = f"""
            INSERT INTO `books` (`snils`, `surname`, `name`, `patronymic`, `in_archive`, `in_request`, `personal`) VALUES ('{snils}', '{surname}', '{name}', '{patronymic}', '1', '0', NULL)
            """
            cursor.execute(query)
            sqlconnection.commit()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Операция выполнена!")
            msg.setInformativeText('Дело зарегистрировано.')
            msg.setWindowTitle("Статус")
            msg.exec_()
            mainWindow.updateTable()
            self.close()

    def closeEvent(self, event):
        self.setWindowModality(QtCore.Qt.ApplicationModal)


class EditBook(QWidget):
    def __init__(self, snils):
        super().__init__()
        uic.loadUi(os.path.join(path, 'editBook.ui'), self)
        self.pushButton.clicked.connect(self.sendNewData)
        self.pushButton_2.clicked.connect(self.close)
        self.pushButton_4.clicked.connect(self.deleteBook)
        self.pushButton_3.clicked.connect(self.returnBook)

        self.snils = snils

        self.lineEdit.setText(self.snils)
        self.lineEdit_7.setText(self.snils)
        self.lineEdit_7.textEdited.connect(self.formatSnils)

        self.pushButton_3.setEnabled(False)

        sqlconnection.commit()
        with sqlconnection.cursor() as cursor:
            query = f'SELECT * FROM books WHERE snils = "{self.snils}"'
            cursor.execute(query)
            row = list(cursor)[0]
            self.surname = row['surname']
            self.name = row['name']
            self.patronymic = row['patronymic']
            self.lineEdit_2.setText(self.surname)
            self.lineEdit_5.setText(self.surname)
            self.lineEdit_3.setText(self.name)
            self.lineEdit_8.setText(self.name)
            self.lineEdit_4.setText(self.patronymic)
            self.lineEdit_6.setText(self.patronymic)

            if row['in_request'] == 1:
                self.lineEdit_9.setText('Запрошено')
                
            else:
                if row['in_archive'] == 1:
                    self.lineEdit_9.setText('В архиве')
                else:
                    username = row['personal']
                    with sqlconnection.cursor() as cursor:
                        query = f"""
                            SELECT * FROM users WHERE username = "{username}"
                        """
                        cursor.execute(query)
                        row = list(cursor)[0]
                        self.lineEdit_9.setText(f"У сотрудника: {row['surname']} {row['name'][0]}. {row['patronymic'][0]}.")
                        self.pushButton_3.setEnabled(True)

    def returnBook(self):
        with sqlconnection.cursor() as cursor:
            query = f"""
                UPDATE books
                SET in_archive = 1
                WHERE snils = "{self.snils}"
            """
            cursor.execute(query)
            sqlconnection.commit()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Операция выполнена!")
            msg.setInformativeText('Дело обновлено.')
            msg.setWindowTitle("Статус")
            msg.exec_()
            self.lineEdit_9.setText('В архиве')
            self.pushButton_3.setEnabled(False)
            mainWindow.updateTable()

    def sendNewData(self):
        snils = self.lineEdit_7.text()

        sqlconnection.commit()
        if snils != self.lineEdit.text():
            with sqlconnection.cursor() as cursor:
                query = f"""
                SELECT snils FROM books WHERE snils = "{snils}"
                """
                cursor.execute(query)
                if len(list(cursor)) > 0:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Ошибка")
                    msg.setInformativeText('Дело с таким СНИЛС уже существует.')
                    msg.setWindowTitle("Ошибка")
                    msg.exec_()
                    return
        
        surname = self.lineEdit_5.text()
        name = self.lineEdit_8.text()
        patronymic = self.lineEdit_6.text()

        if len(snils) * len(surname) * len(name) * len(patronymic) == 0:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка")
            msg.setInformativeText('Заполните все поля!')
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            return
        if len(snils) != 14:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка")
            msg.setInformativeText('СНИЛС должен содержать 11 цифр!')
            msg.setWindowTitle("Ошибка")
            msg.exec_()
            return

        with sqlconnection.cursor() as cursor:
            query = f"""
                UPDATE books
                SET snils = "{snils}",
                    surname = "{surname}",
                    name = "{name}",
                    patronymic = "{patronymic}"
                WHERE snils = "{self.lineEdit.text()}"
            """
            cursor.execute(query)
            sqlconnection.commit()
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Операция выполнена!")
            msg.setInformativeText('Дело обновлено.')
            msg.setWindowTitle("Статус")
            msg.exec_()
            mainWindow.updateTable()
            self.close()
        
    def formatSnils(self, snils):
        newsnils = formatSnils(snils)
        self.lineEdit_7.setText(newsnils)

    def deleteBook(self):
        message = QMessageBox()
        res = message.question(self, '', "Удалить дело?", message.Yes | message.No)
        if res == message.Yes:
            sqlconnection.commit()
            with sqlconnection.cursor() as cursor:
                query = f"""
                    DELETE FROM books WHERE snils = "{self.snils}"
                """
                cursor.execute(query)
                sqlconnection.commit()
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setText("Операция выполнена!")
                msg.setInformativeText('Дело удалено.')
                msg.setWindowTitle("Статус")
                msg.exec_()
                mainWindow.updateTable()
                self.close()

    def closeEvent(self, event):
        self.setWindowModality(QtCore.Qt.ApplicationModal)


class RequestsWindow(QWidget):
    requests = []
    querytype = 0
    # 0 - Inbox
    # 1 - All
    # 2 - Working

    def __init__(self, qtype):
        super().__init__()
        self.querytype = qtype

        if self.querytype == 0:
            uic.loadUi(os.path.join(path, 'requests.ui'), self)
        elif self.querytype == 1:
            uic.loadUi(os.path.join(path, 'allrequests.ui'), self)
        elif self.querytype == 2:
            uic.loadUi(os.path.join(path, 'myrequests.ui'), self)

        self.pushButton.clicked.connect(lambda: openWindow(MainMenu))
        self.pushButton_2.clicked.connect(self.update)
        self.listWidget.itemDoubleClicked.connect(self.clickHandle)

        self.update()

    def update(self):
        requests = []
        self.listWidget.clear()

        sqlconnection.commit()
        with sqlconnection.cursor() as cursor:
            if self.querytype == 0:
                query = f"""
                    SELECT * FROM requests WHERE status = 0
                """
            elif self.querytype == 1:
                query = f"""
                    SELECT * FROM requests
                """
            elif self.querytype == 2:
                query = f"""
                    SELECT * FROM requests WHERE status = 1 and archivist = "{user.username}"
                """
            cursor.execute(query)
            for request in list(cursor):
                requests.append(request['id'])
                books = len(request['books'].split(';'))
                date = request['sendTime']
                formatted = getFormattedUser(request['personal'])
                if request['status'] == 0:
                    item = QListWidgetItem(f"{formatted}. Дел: {books} Отправлена {date} Статус: в очереди")
                elif request['status'] == 1:
                    item = QListWidgetItem(f"{formatted}. Дел: {books} Отправлена {date} Статус: выполняется")
                elif request['status'] == 2:
                    item = QListWidgetItem(f"{formatted}. Дел: {books} Отправлена {date} Статус: выполнена")
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


class InboxRequests(RequestsWindow):
    def __init__(self):
        super().__init__(0)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.setInterval(1000)
        self.timer.start()


class AllRequests(RequestsWindow):
    def __init__(self):
        super().__init__(1)


class MyRequests(RequestsWindow):
    def __init__(self):
        super().__init__(2)


class RequestDetails(QWidget):
    data = dict()

    def __init__(self, details):
        super().__init__()
        uic.loadUi(os.path.join(path, 'requestDetails.ui'), self)

        self.pushButton.clicked.connect(self.close)
        self.pushButton_2.clicked.connect(self.accept)
        self.pushButton_3.clicked.connect(self.printR)
        self.pushButton_4.clicked.connect(self.markAsDone)

        self.lineEdit.setText(str(details['id']))
        self.lineEdit_2.setText(getFormattedUser(details['personal']))
        self.lineEdit_3.setText(str(details['sendTime']))
        if details['archivist'] != "":
            self.lineEdit_6.setText(getFormattedUser(details['archivist']))
        self.textEdit.setText(details['comment'])
        if str(details['receiveTime']) == '0000-00-00 00:00:00':
            self.lineEdit_4.setText('-')
        else:
            self.lineEdit_4.setText(str(details['receiveTime']))

        self.pushButton_2.setEnabled(False)
        self.pushButton_4.setEnabled(False)

        if details['status'] == 0:
            self.lineEdit_5.setText("В очереди")
            self.pushButton_2.setEnabled(True)
        elif details['status'] == 1:
            self.lineEdit_5.setText("Исполняется")
            if user.username == details['archivist']:
                self.pushButton_4.setEnabled(True)
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

    def markAsDone(self):
        sqlconnection.commit()
        with sqlconnection.cursor() as cursor:
            query = f"""
                UPDATE requests
                SET status = 2
                WHERE id = {self.data['id']}
            """
            cursor.execute(query)
            sqlconnection.commit()

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Операция выполнена!")
        msg.setInformativeText('Заявка выполнена.')
        msg.setWindowTitle("Статус")
        msg.exec_()

        self.pushButton_4.setEnabled(False)
        self.lineEdit_5.setText('Выполнена')

    def printR(self):
        self.data['receiveTime'] = time.strftime('%Y-%m-%d %H:%M:%S')
        file = open(os.path.join(path, "checkout.html"), "w")
        booksStr = ""
        books = self.data['books'].split(';')

        for book in books:
            sqlconnection.commit()
            with sqlconnection.cursor() as cursor:
                query = f"""
                    SELECT surname, name, patronymic FROM books
                    WHERE snils = "{book}"
                """
                cursor.execute(query)
                row = list(cursor)[0]
                booksStr += f"<tr><td>{book}</td><td>{row['surname']} {row['name']} {row['patronymic']}</td></tr>"
        checkout = """
            <!DOCTYPE html>
            <body>
                <span style="font-size: 30px;"><strong>Заявка №01.</strong></span><br><br>
                <span style="font-size: 25px;">Запросивший сотрудник: """ + getFormattedUser(self.data['personal']) +  """ </span><br>
                <span style="font-size: 25px;">Время отпраки заявки: """ + str(self.data['sendTime']) +  """</span><br>
                <span style="font-size: 25px;">Время принятия заявки: """ + str(self.data['receiveTime']) +  """</span><br><br>
                <span style="font-size: 25px;"><strong>Дела в заявке:</strong></span><br>
                <style>
                    tr {
                        font-size: 20px;
                    }
                </style>
                <table border="1", cellpadding="5px">
                    <tr>
                        <th>СНИЛС</th>
                        <th>Пенсионер</th>
                    </tr>""" + booksStr + """</table></body></html>"""

        file.write(checkout)
        file.close()
        message = QMessageBox()
        res = message.question(self, '', "Напечатать заявку?", message.Yes | message.No)
        if res == message.Yes:
            os.system(f'RUNDLL32.EXE MSHTML.DLL,PrintHTML "{os.path.join(path, "checkout.html")}"')

    def accept(self):
        self.data['receiveTime'] = time.strftime('%Y-%m-%d %H:%M:%S')
        file = open(os.path.join(path, "checkout.html"), "w")
        booksStr = ""
        books = self.data['books'].split(';')

        for book in books:
            sqlconnection.commit()
            with sqlconnection.cursor() as cursor:
                query = f"""
                    SELECT surname, name, patronymic FROM books
                    WHERE snils = "{book}"
                """
                cursor.execute(query)
                row = list(cursor)[0]
                booksStr += f"<tr><td>{book}</td><td>{row['surname']} {row['name']} {row['patronymic']}</td></tr>"
            with sqlconnection.cursor() as cursor:
                query = f"""
                    UPDATE books
                    SET in_archive = 0,
                        in_request = 0,
                        personal = "{self.data['personal']}"
                    WHERE snils = "{book}"
                """
                cursor.execute(query)
                sqlconnection.commit()
        checkout = """
            <!DOCTYPE html>
            <body>
                <span style="font-size: 30px;"><strong>Заявка №01.</strong></span><br><br>
                <span style="font-size: 25px;">Запросивший сотрудник: """ + getFormattedUser(self.data['personal']) +  """ </span><br>
                <span style="font-size: 25px;">Время отпраки заявки: """ + str(self.data['sendTime']) +  """</span><br>
                <span style="font-size: 25px;">Время принятия заявки: """ + str(self.data['receiveTime']) +  """</span><br><br>
                <span style="font-size: 25px;"><strong>Дела в заявке:</strong></span><br>
                <style>
                    tr {
                        font-size: 20px;
                    }
                </style>
                <table border="1", cellpadding="5px">
                    <tr>
                        <th>СНИЛС</th>
                        <th>Пенсионер</th>
                    </tr>""" + booksStr + """</table></body></html>"""

        file.write(checkout)
        file.close()

        with sqlconnection.cursor() as cursor:
            query = f"""
                UPDATE requests
                SET receiveTime = "{self.data['receiveTime']}",
                    status = 1,
                    archivist = "{user.username}"
                WHERE id = {self.data['id']}
            """
            cursor.execute(query)
            sqlconnection.commit()

        message = QMessageBox()
        res = message.question(self, '', "Напечатать заявку?", message.Yes | message.No)
        if res == message.Yes:
            os.system(f'RUNDLL32.EXE MSHTML.DLL,PrintHTML "{os.path.join(path, "checkout.html")}"')
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Операция выполнена!")
        msg.setInformativeText('Заявка принята.')
        msg.setWindowTitle("Статус")
        msg.exec_()
        self.close()
        mainWindow.update()

    def closeEvent(self, event):
        self.setWindowModality(QtCore.Qt.ApplicationModal)


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