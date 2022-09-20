import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from PyQt5 import QtNetwork as qtn

class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        self.cw = ChatWindow()
        self.setCentralWidget(self.cw)

        # connecting the front end and the backend
        username = qtc.QDir.home().dirName()
        self.interface = UdpChatInterface(username)
        # submitted emits a string that is the message
        # the interface adds the username
        self.cw.submitted.connect(self.interface.send_message)
        # write_message is displaying the actual message when received
        self.interface.received.connect(self.cw.write_message)
        # on error pop-up is summoned with error message
        self.interface.error.connect(lambda x: qtw.QMessageBox.critical(None, 'Error', x))

        # End main UI Code
        self.show()


# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
class ChatWindow(qtw.QWidget):
    submitted = qtc.pyqtSignal(str)
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        self.setLayout(qtw.QGridLayout())
        self.message_view = qtw.QTextEdit(readOnly=True)
        self.layout().addWidget(self.message_view, 1, 1, 1, 2)
        self.message_entry = qtw.QLineEdit()
        self.layout().addWidget(self.message_entry, 2, 1)
        self.send_btn = qtw.QPushButton("Send", clicked = self.send)
        self.layout().addWidget(self.send_btn, 2, 2)

        # End main UI Code
        # self.show()


    def write_message(self, username, message):
        self.message_view.append(f'<b>{username}: </b> {message} <br>')

    def send(self):
        message = self.message_entry.text().strip()
        if message:
            self.submitted.emit(message)
            self.message_entry.clear()


# inherits qtObject so you ccan use signals
# the problem with UDP is you can't really use it outside of local networks
class UdpChatInterface(qtc.QObject):
    port = 7777
    # delimiter is used to seperate usernaem and string so like hello world would be author||Hello world.
    delimiter = "||"
    received = qtc.pyqtSignal(str, str)
    error = qtc.pyqtSignal(str)

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.socket = qtn.QUdpSocket()
        # you have to bind it to a local address and port number
        self.socket.bind(qtn.QHostAddress.Any, self.port)
        # readyRead is the event name, and emitted whenever data is received by the socket
        self.socket.readyRead.connect(self.process_datagrams)
        # again error is the event name
        self.socket.error.connect(self.on_error)

    def on_error(self, socket_error):
        # so first you need to find all errors tied to "SocketError" and then query through them to find your error
        error_index = (qtn.QAbstractSocket.staticMetaObject.indexOfEnumerator('SocketError'))
        # on error you just get a number back and you have to query for the actual error with this method unfortunately
        error = (qtn.QAbstractSocket.staticMetaObject.enumerator(error_index).valueToKey(socket_error))
        # format and send
        message = f"There was a network error: {error}"
        self.error.emit(message)

    def process_datagrams(self):
        # a transmission is known as a datagram
        # transmissions are stored in a buffer so we have to keep reading until we clear the buffer
        while self.socket.hasPendingDatagrams():
            # you get back a bytes object equivalent to python's byte object
            datagram = self.socket.receiveDatagram()
            # this converts the bytes object array to a string
            raw_message = bytes(datagram.data()).decode('utf-8')
            # first we have to check if it's a message we're supposed to receive
            # as in one that contains our delimiter
            if self.delimiter not in raw_message:
                continue
            username, message = raw_message.split(self.delimiter, 1)
            # emit that you received it
            self.received.emit(username, message)

    def send_message(self, message):
        # format the string and then convert it to a bytes object to send
        msg_bytes = f'{self.username}{self.delimiter}{message}'.encode('utf-8')
        self.socket.writeDatagram(qtc.QByteArray(msg_bytes), qtn.QHostAddress.Broadcast, self.port)

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
