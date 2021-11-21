from PyQt5 import QtCore, QtGui, QtWidgets
from mail_ui import Ui_Form
from smtplib import SMTP


class Widget(QtWidgets.QWidget):
    def __init__(self):
        super(Widget, self).__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)


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


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())