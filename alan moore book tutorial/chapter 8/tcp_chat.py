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

        # now to connect our back end and front end
        recipient, _ = qtw.QInputDialog.getText(None, "Recipient", 'Specify the IP or hostname to connect to.')
        if not recipient:
            sys.exit()
        username = qtc.QDir.home().dirName()
        self.interface = TcpChatInterface(username, recipient)
        self.cw.submitted.connect(self.interface.send_message)
        self.interface.received.connect(self.cw.write_message)
        self.interface.error.connect(lambda x: qtw.QMessageBox.critical(None, "Error", x))
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
        self.send_btn = qtw.QPushButton("Send", clicked=self.send)
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


class TcpChatInterface(qtc.QObject):
    port = 7777
    delimiter = "||"
    received = qtc.pyqtSignal(str, str)
    error = qtc.pyqtSignal(str)

    def __init__(self, username, recipient):
        super().__init__()
        self.username = username
        self.recipient = recipient
        # listener is for receiving data from other sockets
        self.listener = qtn.QTcpServer()
        self.listener.listen(qtn.QHostAddress.Any, self.port)
        # if there's an error the acceptError event happens
        self.listener.acceptError.connect(self.on_error)
        # new connection is when a new connection is established, like someone else joining the chat
        self.listener.newConnection.connect(self.on_connection)
        self.connections = []

        # now this is for sending data from this socket to others
        # note we don't need to bind this socket because it won't be listening
        self.client_socket = qtn.QTcpSocket()
        self.client_socket.error.connect(self.on_error)



    # same error system as UDP
    def on_error(self, socket_error):
        # so first you need to find all errors tied to "SocketError" and then query through them to find your error
        error_index = (qtn.QAbstractSocket.staticMetaObject.indexOfEnumerator('SocketError'))
        # on error you just get a number back and you have to query for the actual error with this method unfortunately
        error = (qtn.QAbstractSocket.staticMetaObject.enumerator(error_index).valueToKey(socket_error))
        # format and send
        message = f"There was a network error: {error}"
        self.error.emit(message)

    def on_connection(self):
        # returns the next waiting connection as a QTcpSocket object
        connection = self.listener.nextPendingConnection()
        # it emits a readyRead signal when it receives data just like UDP
        connection.readyRead.connect(self.process_datastream)
        # save the new socket somewhere
        self.connections.append(connection)

    def process_datastream(self):
        for socket in self.connections:
            # this wrapper sets up a smaller interface for us to handle writing/reading
            self.datastream = qtc.QDataStream(socket)
            # continue skips to the next thing in the loop, without running any further code below it
            if not socket.bytesAvailable():
                continue
            # IMPORTANT QString does not return a Qstring object it returns a unicode string. It's important
            #  to know that this method only works if a QString was sent with the original packets,
            #  if something else was sent it won't be able to read it!!!!
            message_length = self.datastream.readInt32()
            print(message_length)
            raw_message = self.datastream.readQString()
            # if it exists, split and send
            if raw_message and self.delimiter in raw_message:
                username, message = raw_message.split(self.delimiter, 1)
                self.received.emit(username, message)

    def send_message(self, message):
        raw_message = f'{self.username}{self.delimiter}{message}'
        socket_state = self.client_socket.state()
        # check if it's already connected to a recipient if not connect it
        if socket_state != qtn.QAbstractSocket.ConnectedState:
            self.client_socket.connectToHost(self.recipient, self.port)
        # now we can somewhat safely assume we're connected
        self.datastream = qtc.QDataStream(self.client_socket)
        # datastream values can only be pulled in order of what we sent, kinda obvious tho
        # first we send the string length then the string itself
        # we need to make sure we handle that IN ORDER in our process data stream function
        self.datastream.writeUInt32(len(raw_message))
        self.datastream.writeQString(raw_message)
        self.received.emit(self.username, message)


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
