import sys
from tools import DIR_PELIS,DIR_SERIES,setconfig
from PyQt5.QtWidgets import (QMainWindow, QTextEdit,
    QDialog, QFileDialog, QApplication, QVBoxLayout, QLineEdit,QPushButton)
from PyQt5.QtGui import QIcon



class Directori(QFileDialog):
    def __init__(self, tipus):
        super().__init__()
        fname = QFileDialog.getExistingDirectory(self, 'select directory', '/home')
        print('dir:', fname)
        if fname:
            if tipus == 1:
                DIR_SERIES = fname
                setconfig(dir_series = str(DIR_SERIES))
            elif tipus == 2:
                DIR_PELIS = fname
                setconfig(dir_pelis = str(DIR_PELIS))


    def quit(self):
        #pop up goodBye dialog
        self.close()
    def closeEvent(self, QCloseEvent):
        print('closing..')


class TVisoLogin(QDialog):
    def __init__(self):
        QDialog.__init__(self)
        self.textName = QLineEdit(self)
        self.textPass = QLineEdit(self)
        self.textPass.setEchoMode(QLineEdit.Password)
        self.buttonLogin = QPushButton('Login', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        layout = QVBoxLayout(self)
        layout.addWidget(self.textName)
        layout.addWidget(self.textPass)
        layout.addWidget(self.buttonLogin)
    # TODO encriptar contrasenyes
    def handleLogin(self):
        if (self.textName.text() != '' and
            len(self.textPass.text()) >=7):
            setconfig(usuari = self.textName.text(), password = self.textPass.text() )
            self.accept()

def logingTviso():
    ex = TVisoLogin()
    ex.show()
    ex.raise_()
def dialegdirector(tipus):

    # app = QApplication(sys.argv)
    ex = Directori(tipus)
    # app.exit()


