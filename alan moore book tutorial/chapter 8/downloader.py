import sys
from os import path
from PyQt5 import QtNetwork as qtn
from PyQt5 import QtCore as qtc




# pretty pointless but it lets you download any page, the HTML or whatever it provides not the contents of it
class Downloader(qtc.QObject):
    def __init__(self, url):
        super().__init__()
        # we create a newtork access manager
        self.manager = qtn.QNetworkAccessManager(finished=self.on_finished)
        # then send a get request which will download whatever it was
        self.request = qtn.QNetworkRequest(qtc.QUrl(url))
        self.manager.get(self.request)

    # the reply object here is QNetworkReply object, which contains the dat and metadata from the remote server
    def on_finished(self, reply):
        # sometimes filename doesn't exist so if it doesn't just leave it as 'download'
        filename = reply.url().fileName() or 'download'
        if path.exists(filename):
            print('File already exists, not overwriting.')
            sys.exit(1)
        # notice wb, which is write binary, readAll returns a binary data in the form of a QByteArray
        with open(filename, 'wb') as fh:
            fh.write(reply.readAll())
        print(f"{filename} written")
        sys.exit(0)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f'Usage: {sys.argv[0]} <download url>')
        sys.exit(1)
    # QCore is used for non GUI stuff
    app = qtc.QCoreApplication(sys.argv)
    d = Downloader(sys.argv[1])
    sys.exit(app.exec_())