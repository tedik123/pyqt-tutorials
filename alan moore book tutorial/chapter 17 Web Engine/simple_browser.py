import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from PyQt5 import QtWebEngineWidgets as qtwe


# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
# idk how helpful this is but:
# https://doc.bccnsoft.com/docs/PyQt5/pyqt4_differences.html#pyuic5
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        navigation = self.addToolBar('Navigation')
        style = self.style()
        self.setWindowTitle("Not A Virus Browser")
        self.setWindowIcon(qtg.QIcon("ie.svg"))
        self.back = navigation.addAction('Back')
        self.back.setIcon(style.standardIcon(style.SP_ArrowBack))
        self.forward = navigation.addAction('Forward')
        self.forward.setIcon(style.standardIcon(style.SP_ArrowForward))
        self.reload = navigation.addAction('Reload')
        self.reload.setIcon(style.standardIcon(style.SP_BrowserReload))
        self.stop = navigation.addAction('Stop')
        self.stop.setIcon(style.standardIcon(style.SP_BrowserStop))
        self.urlbar = qtw.QLineEdit()
        navigation.addWidget(self.urlbar)
        self.go = navigation.addAction('Go')
        self.go.setIcon(style.standardIcon(style.SP_DialogOkButton))

        # webview = qtwe.QWebEngineView()
        # self.setCentralWidget(webview)
        # webview.load(qtc.QUrl('https://www.google.com'))
        # # to establish navigating to other pages
        # self.go.triggered.connect(lambda : webview.load(qtc.QUrl(self.urlbar.text())))
        # # fortunately a lot of common actions already have functions for you
        # self.back.triggered.connect(webview.back)
        # self.forward.triggered.connect(webview.forward)
        # self.reload.triggered.connect(webview.reload)
        # self.stop.triggered.connect(webview.stop)

        self.tabs = qtw.QTabWidget(tabsClosable=True, movable=True)
        self.tabs.tabCloseRequested.connect(self.tabs.removeTab)
        self.new = qtw.QPushButton('New')
        self.tabs.setCornerWidget(self.new)
        self.setCentralWidget(self.tabs)

        # add our custom methods
        self.back.triggered.connect(self.on_back)
        self.forward.triggered.connect(self.on_forward)
        self.reload.triggered.connect(self.on_reload)
        self.stop.triggered.connect(self.on_stop)
        self.go.triggered.connect(self.on_go)
        self.urlbar.returnPressed.connect(self.on_go)
        self.new.clicked.connect(self.add_tab)

        # in order to ensure session information is stored we need to save the profile and share that between tabs
        # otherwise each new tab will forget your login information or anything relevant like that
        self.profile = qtwe.QWebEngineProfile()
        # we need to associate the profile with each new webview
        # they're not actually a property of webview but rather the property of QWebEnginePage which can be thought
        # of as a model for the web view
        # which we'll do in the add tab function

        self.history_dock = qtw.QDockWidget('History')
        self.addDockWidget(qtc.Qt.RightDockWidgetArea, self.history_dock)
        self.history_list = qtw.QListWidget()
        # this will simply display the history of the currently selected tab
        self.history_dock.setWidget(self.history_list)
        self.history_dock.hide()
        # need to change the history display based on the tab
        self.tabs.currentChanged.connect(self.update_history)

        # now connect to the navigate history
        self.history_list.itemDoubleClicked.connect(self.navigate_history)
        # to establish dock widget history interaction
        self.first_release = False
        self.key_list = []

        # you can change a lot about the experience through the settings object
        # this is a GLOBAL object it doesn't need to be assigned to webview or webEngine
        settings = qtwe.QWebEngineSettings.defaultSettings()
        # change all instances of sansseriffont with impact font
        # if you want you can change the font size or defaultTextEncoding
        settings.setFontFamily(qtwe.QWebEngineSettings.SansSerifFont, 'Impact')

        settings.setAttribute(qtwe.QWebEngineSettings.PluginsEnabled,True)
        settings.setAttribute(qtwe.QWebEngineSettings.FullScreenSupportEnabled, True)
        # IMPORTANT to alter per page settings you can use page.settings()

        # let's add a text search function
        # the cool thing about QWebEngine is that we can inject our own JS scripts into the browser to add
        # unique functionality
        self.find_dock = qtw.QDockWidget('Search')
        self.addDockWidget(qtc.Qt.BottomDockWidgetArea, self.find_dock)
        self.find_text = qtw.QLineEdit()
        self.find_dock.setWidget(self.find_text)
        self.find_text.textChanged.connect(self.text_search)
        # you need to also set what child gets the focus if the parent is being called into focus!
        self.find_dock.setFocusProxy(self.find_text)
        self.find_dock.hide()

        # so we'll read in our JS file and save it as a variable
        with open('finder.js', 'r') as fh:
            self.finder_js = fh.read()

        # to have our scripts run globally we need to manipulate the QWebEngineScripts object
        self.finder_script = qtwe.QWebEngineScript()
        self.finder_script.setSourceCode(self.finder_js)
        # scripts are run in one of 256 worlds, which are isolated to guarantee future function calls within the script
        # run in the same world we need to set it
        # otherwise EACH function call will run in it's OWN world!
        self.finder_script.setWorldId(qtwe.QWebEngineScript.MainWorld)
        # then to add this script function we need to change the add_tab function

        # create the first tab
        self.add_tab()
        # End main UI Code
        self.show()

    # the way this is now, it redefines the functions every time you update the search bar
    # obviously not very efficient
    # def text_search(self, term):
    #     term = term.replace('"', '')
    #     page = self.tabs.currentWidget().page()
    #     # takes a string to run
    #     page.runJavaScript(self.finder_js)
    #     js = f'highlight_term("{term}");'
    #     # takes a string to run
    #     page.runJavaScript(js)

    def text_search(self, term):
        page = self.tabs.currentWidget().page()
        # execute the function we want with the correct function call
        # takes a string to run
        js = f'highlight_term("{term}");'
        # page.runJavaScript(js)
        # to access the return value we need to pass a reference to a python callable as a second argument
        page.runJavaScript(js, self.match_count)

    def match_count(self,count):
        if count:
            self.statusBar().showMessage(f'{count} matches')
        else:
            self.statusBar().clearMessage()

    def keyPressEvent(self, event):
        self.first_release = True
        astr = event.key()
        self.key_list.append(astr)

    def keyReleaseEvent(self, event):
        if self.first_release:
            self.processmultikeys(self.key_list)
        self.first_release = False



    def processmultikeys(self, keylist):
        # print(keylist)
        if len(keylist) >= 2:
            # print(keylist[-1])
            if keylist[-2] == qtc.Qt.Key.Key_Control and keylist[-1] == qtc.Qt.Key.Key_H:
                self.history_dock.show()

            if keylist[-2] == qtc.Qt.Key.Key_Control and keylist[-1] == qtc.Qt.Key.Key_F:
                self.find_dock.show()
                self.find_dock.setFocus()

            self.key_list = []
        self.key_list = []

    def add_tab(self, *args):
        # simply create a new webview and add it to the tabs
        webview = qtwe.QWebEngineView()
        tab_index = self.tabs.addTab(webview, 'New Tab')
        # you must pass in a profile, there's no way to set it after the object is created
        page = qtwe.QWebEnginePage(self.profile)
        # we also add the script to the page for each new page created
        page.scripts().insert(self.finder_script)
        # to assign it to the webview we simply set it
        webview.setPage(page)
        # emitted when a new url is loaded(!)
        webview.urlChanged.connect(lambda x: self.tabs.setTabText(tab_index, x.toString()))
        webview.urlChanged.connect(lambda x: self.urlbar.setText(x.toString()))
        # need to update the history when a new tab is created as well
        webview.urlChanged.connect(self.update_history)

        # set default page
        webview.setHtml('<h1>Blank Tabs</h1><p>It is a blank tab</p>', qtc.QUrl('about:blank'))

        # this is so when we click on links that are supposed to open a new tab, that actually happens
        webview.createWindow = self.add_tab
        return webview

    def update_history(self, *args):
        self.history_list.clear()
        webview = self.tabs.currentWidget()
        if webview:
            # history is QWebEnginehistory object
            # when forward and back are called webview history is consulted
            history = webview.history()
            for history_item in reversed(history.items()):
                list_item = qtw.QListWidgetItem()
                # we're using set data as this will automatically convert the URL object to a string
                list_item.setData(qtc.Qt.DisplayRole, history_item.url())
                self.history_list.addItem(list_item)

    # double clicked will pass in the QlistWidget item that was clicked and we simply get the url and load it
    def navigate_history(self, item):
        # data is the url accessor method
        qurl = item.data(qtc.Qt.DisplayRole)
        if self.tabs.currentWidget():
            self.tabs.currentWidget().load(qurl)

    # since we have multiple tabs we need to make slots that trigger the change on the correct tab
    def on_back(self):
        # since current widget just returns the widget we can access the back or any relevant method directly like this
        self.tabs.currentWidget().back()

    def on_forward(self):
        self.tabs.currentWidget().forward()

    def on_reload(self):
        self.tabs.currentWidget().reload()

    def on_stop(self):
        self.tabs.currentWidget().stop()

    def on_go(self):
        url = self.urlbar.text()
        if url.startswith(('https://www.', 'http://www.')):
            pass
        elif url.startswith('www.'):
            url = 'https://' + url
        else:
            url = 'https://www.' + url
        self.tabs.currentWidget().load(qtc.QUrl(url))


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
