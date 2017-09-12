import socket
import sys
from multiprocessing.pool import Pool, ThreadPool

from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy

from mainwindow import Ui_MainWindow


class DownloadThread(QtCore.QThread):
    data_downloaded = QtCore.pyqtSignal(object)

    def __init__(self, text_from_combobox):
        QtCore.QThread.__init__(self)
        self.text_from_combobox = text_from_combobox

    def run(self):
        self.host = socket.gethostname()
        self.port = 12345
        self.s = socket.socket()
        self.s.connect((self.host, self.port))
        print("Sending", self.text_from_combobox)
        if self.text_from_combobox == "Carnival Australia":
            self.s.send(str.encode("Carnival-AU"))
        else:
            self.s.send(str.encode(self.text_from_combobox))
        response = self.s.recv(1024).decode("utf-8")
        if 'Success' in response:
            print(response)
        else:
            response = response.split()[0] + " Failed!"
        self.data_downloaded.emit(response)

        self.s.close()


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.threads = []
        self.setupUi(self)
        self.pushButton.clicked.connect(self.start)

    def start(self):
        self.label_2.clear()
        self.label.setText("Downloading, Please wait...")
        movie = QMovie("giphy.gif")
        self.label_2.setAttribute(QtCore.Qt.WA_NoSystemBackground)
        self.label_2.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.label_2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label_2.setScaledContents(True)
        self.label_2.setMovie(movie)
        movie.start()
        text = self.comboBox.currentText()
        if text in "All":
            all_items = [self.comboBox.itemText(i) for i in range(self.comboBox.count())]
            values = []
            for item in all_items:
                if item is not 'None' or item is not 'A' or item is not "l" or item is not 'All':
                    if item == "Carnaval Australia":
                        values.append("Carnival-AU")
                    elif item == "Carnaval.com":
                        values.append("Carnival-US")
                    elif item == "Holland America":
                        values.append("Holland-America")
                    elif item == "Norwegian Cruise Lines":
                        values.append('NCL')
                    elif item == "Oceania Cruises Non Cruise only prices":
                        values.append('OceaniaCruises')
                    elif item == "Oceania Cruises Cruise only prices":
                        values.append('OceaniaCruisesCRP')
                    elif item == "P&O Australia":
                        values.append('P-O-AU')
                    elif item == "P&O UK":
                        values.append('P-O-UK')
                    elif item == "Royal Caribbean":
                        values.append('Royal-Caribbean')
                    else:
                        values.append(item)
            values.pop()
            values.pop(0)
            text = values
        else:
            text = [text]
        self.send(text)

    def send(self, text_from_combobox):
        self.threads = []
        for arg in text_from_combobox:
            downloader = DownloadThread(arg)
            downloader.data_downloaded.connect(self.on_data_ready)
            self.threads.append(downloader)
            downloader.start()

    def on_data_ready(self, data):
        if 'Success' in data:
            self.label.setText(data)
            self.label_2.clear()
            self.label_2.setPixmap(QtGui.QPixmap('done.gif'))
        else:
            self.label.setText(data)
            self.label_2.clear()
            self.label_2.setPixmap(QtGui.QPixmap('failed.png'))

def main():
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
