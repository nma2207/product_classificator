from view_control import Application
from PyQt5 import QtWidgets

import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    view = Application()
    view.show()
    sys.exit(app.exec_())

#python -m PyQt5.uic.pyuic -x NAS_main.ui -o view_ui.py
#python -m PyQt5.uic.pyuic -x mail.ui -o mail_ui.py