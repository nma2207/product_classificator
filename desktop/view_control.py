from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from view_ui import Ui_MainWindow
from mail_ui import Ui_Form
from view_dialog import QuestDialog, WarningDialog, WarningDialogExpand
import os
import pandas as pd
from ft import FastTextModel
from clickablelineedit  import  ClickableLineEdit


# класс для делегирования(выравнивание по центру)
class AlignDelegate(QtWidgets.QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate, self).initStyleOption(option, index)
        option.displayAlignment = QtCore.Qt.AlignCenter

# Класс для заполнения табличного представления фреймом данных pandas
class PandasModel(QtCore.QAbstractTableModel):
    def __init__(self, data, parent=None):
        QtCore.QAbstractTableModel.__init__(self, parent)
        self._data = data
    def rowCount(self, parent=None):
        return len(self._data.values)
    def columnCount(self, parent=None):
        return self._data.columns.size
    def data(self, index, role=QtCore.Qt.DisplayRole):
        if index.isValid():
            if role == QtCore.Qt.DisplayRole:
                return str(self._data.iloc[index.row()][index.column()])
        return None
    def headerData(self, col, orientation, role):
        if orientation == QtCore.Qt.Horizontal and role == QtCore.Qt.DisplayRole:
            return self._data.columns[col]
        return None


# Настройка приложения
class Application(QtWidgets.QMainWindow):
    def __init__(self):
        super(Application, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowState(QtCore.Qt.WindowMaximized)

        self.mail = Mail(self)

        # начальные условия
        if os.path.exists('data.db'):
            self.update_historyTable()

        self.numList = 1
        # изображение в качестве фона

        # клавиши 1 вкладка
        self.ui.openFilesBut.clicked.connect(self.openDirectory)
        self.ui.treeFolder.clicked.connect(self.on_tree_click)
        self.ui.btnSendProcessing.clicked.connect(self.sendProcessing)
        self.ui.exportLiveTradesButton.clicked.connect(self.file_save)
        self.ui.backBtn.clicked.connect(self.backList)
        self.ui.forwardBtn.clicked.connect(self.forwardList)
        self.ui.listEdit.returnPressed.connect(self.listEditGet)
        self.ui.btnSendProcessingAll.clicked.connect(self.sendProcessingAll)
        self.ui.listEdit.clicked.connect(self.clearLE)
        self.ui.btnRefuse.clicked.connect(self.refuseBlank)
        self.ui.backBtn.setEnabled(False)
        self.ui.forwardBtn.setEnabled(False)
        self.ui.listEdit.setEnabled(False)


    def refuseBlank(self):
        self.mail.show()

    def backList(self):
        self.numList -= 1
        self.updownList()

    def forwardList(self):
        self.numList += 1
        self.updownList()

    def openDirectory(self):
        self.dir = QtWidgets.QFileDialog.getExistingDirectory(self)
        #self.dir = 'C:\\Users\\User\\PycharmProjects\\NAS\\csv'
        self.model = QtWidgets.QFileSystemModel()
        self.model.setNameFilters(["*.xls", "*.xlsx", "*.csv"])
        self.model.setRootPath('')
        self.ui.treeFolder.setModel(self.model)
        self.ui.treeFolder.setRootIndex(self.model.index(self.dir))
        self.model.setNameFilterDisables(False)
        self.ui.treeFolder.setColumnWidth(0, 245)
        self.ui.treeFolder.setColumnWidth(3, 75)
        self.ui.treeFolder.setColumnHidden(1, True)
        self.ui.treeFolder.setColumnHidden(2, True)
        self.ui.treeFolder.setIconSize(QtCore.QSize(32,32))

    def updateTable(self, date):
        if len(date) == 0:
            dlg = WarningDialog(self)
            dlg.exec()
        else:
            self.modelTable = PandasModel(date)
            self.ui.tableFileUpdate.setModel(self.modelTable)
            delegate = AlignDelegate(self.ui.tableFileUpdate)
            self.ui.tableFileUpdate.setColumnWidth(0, 80)
            self.ui.tableFileUpdate.setColumnWidth(1, 700)
            self.ui.tableFileUpdate.setColumnWidth(2, 193)
            self.ui.tableFileUpdate.setColumnWidth(3, 500)
            # self.ui.tableFileUpdate.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
            # self.ui.tableFileUpdate.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.Alignment(QtCore.Qt.TextWordWrap))
            self.ui.tableFileUpdate.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.Alignment(QtCore.Qt.TextWordWrap))
            self.ui.tableFileUpdate.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
            self.ui.tableFileUpdate.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
            self.ui.tableFileUpdate.setItemDelegateForColumn(0, delegate)
            self.ui.tableFileUpdate.setItemDelegateForColumn(2, delegate)

    def on_tree_click(self, index):
        file_name = self.model.filePath(index)
        if os.path.splitext(file_name)[-1] == '.csv':
            self.date = pd.read_csv(file_name)
        if os.path.splitext(file_name)[-1] in ['.xls', '.xlsx']:
            self.date = pd.read_excel(file_name)
        self.updownList()

    def updownList(self):
        date = self.date
        size = len(self.date)

        # размерность 1 листа
        sumlist = 100
        self.lstSum = size // 100 + 1
        ost = size - sumlist * self.numList
        if ost < 0:
            lstZero = sumlist * (self.numList - 1)
            lstPast = lstZero + sumlist + ost
        else:
            lstZero = (self.numList - 1) * 100
            lstPast = self.numList * 100

        if self.numList == 1:
            self.ui.backBtn.setEnabled(False)
            self.ui.forwardBtn.setEnabled(True)

        if self.numList == self.lstSum:
            self.ui.backBtn.setEnabled(True)
            self.ui.forwardBtn.setEnabled(False)

        if self.lstSum == 1:
            self.ui.backBtn.setEnabled(False)
            self.ui.forwardBtn.setEnabled(False)

        self.ui.listEdit.setText('{0} страница из {1}'.format(self.numList, self.lstSum))
        self.ui.listEdit.setEnabled(True)
        self.updateTable(date.iloc[lstZero:lstPast])

    def listEditGet(self):
        if int(self.ui.listEdit.text()) > self.lstSum:
            self.numList = self.lstSum
        elif int(self.ui.listEdit.text()) < 1:
            self.numList = 1
        else:
            self.numList = int(self.ui.listEdit.text())
        self.updownList()

    def clearLE(self):
        self.ui.listEdit.clear()

    def sendProcessing(self):
        rows = sorted(set(index.row() for index in self.ui.tableFileUpdate.selectedIndexes()))
        dfs = []
        self.delRow = []
        for row in rows:
            self.delRow.append(row)
            df = self.date.iloc[[row]]
            dfs.append(df)
        df = pd.concat(dfs)
        m = FastTextModel('csv/Реестр деклараций ПОСУДА ЕП РФ без 4000-8500.xlsx')
        if os.path.exists('data.db'):
            res = pd.concat([pd.read_csv('data.db'), m.predict_df(df)], ignore_index=True)
            os.remove('data.db')
            res.to_csv('data.db', index=False)
        else:
            res = m.predict_df(df)
            res.to_csv('data.db', index=False)
        self.update_historyTable()
        self.deleteDataframe()

    def sendProcessingAll(self):
        df = self.date
        m = FastTextModel('csv/Реестр деклараций ПОСУДА ЕП РФ без 4000-8500.xlsx')
        if os.path.exists('data.db'):
            res = pd.concat([pd.read_csv('data.db'), m.predict_df(df)], ignore_index=True)
            os.remove('data.db')
            res.to_csv('data.db', index=False)
        else:
            res = m.predict_df(df)
            res.to_csv('data.db', index=False)
        self.update_historyTable()
        dlg = WarningDialogExpand(self)
        dlg.exec()

    def update_historyTable(self):
        self.modelTableHist = PandasModel(pd.read_csv('data.db'))
        self.ui.historyTable.setModel(self.modelTableHist)
        delegate = AlignDelegate(self.ui.tableFileUpdate)
        self.ui.historyTable.setColumnWidth(0, 80)
        self.ui.historyTable.setColumnWidth(1, 532)
        self.ui.historyTable.setColumnWidth(2, 180)
        self.ui.historyTable.setColumnWidth(3, 380)
        self.ui.historyTable.setColumnWidth(4, 180)
        self.ui.historyTable.setColumnWidth(5, 380)
        self.ui.historyTable.setColumnWidth(6, 100)
        # self.ui.historyTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Fixed)
        # self.ui.historyTable.horizontalHeader().setDefaultAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.Alignment(QtCore.Qt.TextWordWrap))
        self.ui.historyTable.setSelectionBehavior(QtWidgets.QTableView.SelectRows)
        self.ui.historyTable.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.ui.historyTable.setItemDelegateForColumn(0, delegate)
        self.ui.historyTable.setItemDelegateForColumn(2, delegate)
        self.ui.historyTable.setItemDelegateForColumn(4, delegate)
        self.ui.historyTable.setItemDelegateForColumn(6, delegate)

    def deleteDataframe(self):
        dlg = QuestDialog(self)
        if dlg.exec():
            self.date.drop(labels=self.delRow, axis=0, inplace=True)
            self.updateTable(self.date)
        else:
            pass

    def file_save(self):
        import shutil
        name = QtWidgets.QFileDialog.getSaveFileName(self, 'Экспортировать файл в csv', filter="Табличное представление (*.csv)")
        shutil.copyfile('data.db', name[0])


class Mail(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.setFixedSize(600, 400)



        self.ui.pushButton.clicked.connect(self.sendMail)
        self.ui.showPasswordBox.stateChanged.connect(self.showPwStateChanged)
        self.ui.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)

        # QtCore.QMetaObject.connectSlotsByName(Form)

    def sendMail(self):
        firstLen = len(self.ui.receiverLineEdit.text())
        secondLen = len(self.ui.messageTextEdit.toPlainText())
        thirdLen = len(self.ui.subjectLineEdit.text())
        fourthLen = len(self.ui.senderLineEdit.text())
        fifthLen = len(self.ui.passwordLineEdit.text())

        sender = self.ui.senderLineEdit.text()
        receiver = self.ui.receiverLineEdit.text()
        if firstLen and secondLen and thirdLen and fourthLen and fifthLen != 0:
            if "@" and ".com" in receiver and "@" and ".com" in sender:
                try:
                    sender = self.ui.senderLineEdit.text()
                    password = self.ui.passwordLineEdit.text()
                    receiver = self.ui.receiverLineEdit.text()
                    subject = self.ui.subjectLineEdit.text()
                    messageText = self.ui.messageTextEdit.toPlainText()

                    smtp = smtplib.SMTP('smtp.gmail.com', 587)
                    smtp.ehlo()
                    smtp.starttls()
                    smtp.ehlo()

                    smtp.login(sender, password)
                    message = ("Subject: " + subject + "\n" + messageText)
                    smtp.sendmail(sender, receiver, message.encode("utf8"))

                    self.ui.sentOrErrorLabel.setText("Email sent.")
                    smtp.quit()
                except smtplib.SMTPAuthenticationError as e:
                    self.ui.sentOrErrorLabel.setText("Username and password does not match.")
                    print(
                        str(e) + "\nIf you can't solve the problem, please contact with me by T4XE#0610 discord address.")
                except smtplib.SMTPServerDisconnected as e:
                    self.ui.sentOrErrorLabel.setText("Server unexpectedly disconnected.")
                    print(
                        str(e) + "\nIf you can't solve the problem, please contact with me by T4XE#0610 discord address.")
                except smtplib.SMTPDataError as e:
                    self.ui.sentOrErrorLabel.setText("The SMTP server refused to accept the message data.")
                    print(
                        str(e) + "\nIf you can't solve the problem, please contact with me by T4XE#0610 discord address.")
                except smtplib.SMTPSenderRefused as e:
                    self.ui.sentOrErrorLabel.setText("Sender address refused.")
                    print(
                        str(e) + "\nIf you can't solve the problem, please contact with me by T4XE#0610 discord address.")
                except smtplib.SMTPRecipientsRefused as e:
                    self.ui.sentOrErrorLabel.setText("All recipient addresses refused.")
                    print(
                        str(e) + "\nIf you can't solve the problem, please contact with me by T4XE#0610 discord address.")
                except smtplib.SMTPNotSupportedError as e:
                    self.ui.sentOrErrorLabel.setText("The command or option attempted is not supported by the server.")
                    print(
                        str(e) + "\nIf you can't solve the problem, please contact with me by T4XE#0610 discord address.")
                except smtplib.SMTPConnectError as e:
                    self.ui.sentOrErrorLabel.setText(
                        "Error occurred during establishment of a connection with the server.")
                    print(
                        str(e) + "\nIf you can't solve the problem, please contact with me by T4XE#0610 discord address.")
                except smtplib.SMTPHeloError as e:
                    self.ui.sentOrErrorLabel.setText("The server refused our HELO message.")
                    print(
                        str(e) + "\nIf you can't solve the problem, please contact with me by T4XE#0610 discord address.")
            else:
                self.ui.sentOrErrorLabel.setText("Please enter correct addresses.")
        else:
            self.ui.sentOrErrorLabel.setText("Please fill all fields.")

    def showPwStateChanged(self):
        if self.ui.showPasswordBox.isChecked():
            self.ui.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Normal)
        else:
            self.ui.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)






















