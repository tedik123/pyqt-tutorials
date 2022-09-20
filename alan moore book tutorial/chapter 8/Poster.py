import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from PyQt5 import QtNetwork as qtn

class Poster(qtc.QObject):
    # reply received will be what we get as a reply from the server we're posting too
    # and will carry with it a string
    replyReceived = qtc.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.nam = qtn.QNetworkAccessManager()
        # finished passes a QNetworkReply object
        self.nam.finished.connect(self.on_reply)


    def on_reply(self, reply):
        # again we get bytes back
        reply_bytes = reply.readAll()
        # convert the bytes to python bytes, and then to utf-8 text
        reply_string = bytes(reply_bytes).decode('utf-8')
        self.replyReceived.emit(reply_string)

    def make_request(self, url, data, filename):
        # first we create the request object
        self.request = qtn.QNetworkRequest(url)
        # then we need to add the payload
        # there's a lot of different types look them up for more info
        # multipart is a container for HTTP parts objects that we need to manually create
        self.multipart = qtn.QHttpMultiPart(qtn.QHttpMultiPart.FormDataType)
        # key value pairs
        for key, value in (data or {}).items():
            http_part = qtn.QHttpPart()
            # contentdisposition is just what type of data it contains
            http_part.setHeader(qtn.QNetworkRequest.ContentDispositionHeader,
                                f'form-data; name="{key}"')
            http_part.setBody(value.encode('utf-8'))
            self.multipart.append(http_part)

        # now to include the filename
        if filename:
            file_part = qtn.QHttpPart()
            file_part.setHeader(qtn.QNetworkRequest.ContentDispositionHeader,
                                f'form-data; name="attachment"; filename="{filename}"')
            # reading the file as binary
            filedata = open(filename, 'rb').read()
            # set body expects bytes/binary!
            file_part.setBody(filedata)
            self.multipart.append(file_part)
        # now send the actual post request
        self.nam.post(self.request, self.multipart)
