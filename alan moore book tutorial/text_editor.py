import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
from PyQt5.QtGui import QPalette, QColor


class MainWindow(qtw.QMainWindow):
    # settings = {'show_warnings' : True}
    # with QSettings object it saves it differently depending on the platform
    settings = qtc.QSettings("Tedi K", 'text editor') #on linux it saves as .conf file somewhere
    # simply replacing it with QSettings object allows us to have a persistent saved settings format
    # without having to worry about I/O of any kind!
    # though it is limited with what it can save, it can't save objects,
    # but it can save just about any type of python data class
    # also it cannot tell what the type of the data saved is so on retrieval, you must pass in a type as well

    def show_settings(self):
        settings_dialog = SettingsDialog(self.settings, self)
        settings_dialog.exec()

    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        # with the main window there is a central widget where most if not all the widgets should go into
        # other parts of the main window are outside the central widget but these are added automatically
        # there can only be ONE widget inside a central widget but that doesn't mean it can't be a nested widget
        self.textEdit = qtw.QTextEdit()
        self.setCentralWidget(self.textEdit)
        # to create a status bar one way is this:
        # status_bar = qtw.QStatusBar()
        # self.setStatusBar(status_bar)
        # status_bar.showMessage("Welcome to text_editor.py")

        # a better way to create the status bar
        # this is because status bar is automatically created if one doesn't exist already
        self.statusBar().showMessage("Welcome to text_editor.py")

        # let's make it so the status bar keeps track of our character count
        charcount_label = qtw.QLabel("chars: 0")
        self.textEdit.textChanged.connect(lambda: charcount_label.setText(
            "chars: " +
            str(len(self.textEdit.toPlainText()))
        ))
        wordcount_label = qtw.QLabel("Word Count: 0")
        self.textEdit.textChanged.connect(lambda: wordcount_label.setText(
            "Word Count:" +
            str(len(self.textEdit.toPlainText().split()))
        ))
        # you have 2 options for adding widgets to the status bar
        # regular (using .addWidget() or .insertWidget() ) where widgets will be covered up by long status messages
        # permanent where the widget will remain visible over the status message
        self.statusBar().addPermanentWidget(wordcount_label)
        self.statusBar().addPermanentWidget(charcount_label)

        # much like statusbar one will be created if it doesn't exist already, menu bar is the top area
        menubar = self.menuBar()
        # to add sub menus
        file_menu = menubar.addMenu("File")  # this is the main header
        edit_menu = file_menu.addMenu("Edit")  # these are subheaders to the file_menu, it returns the menu object
        help_menu = file_menu.addMenu("Help")

        # to populate the menu with items you use action objects that will run some code when clicked
        # to be useful it needs a name and a callback function, you can also define a keyboard shortcut and an icon
        open_action = file_menu.addAction('Open')
        save_action = file_menu.addAction('Save')
        quit_action = file_menu.addAction('Quit', self.close)
        edit_menu.addAction("Undo", self.textEdit.undo)

        redo_action = qtw.QAction('Redo', self) #you need to pass in a parent otherwise it will not show
        redo_action.triggered.connect(self.textEdit.redo)
        edit_menu.addAction(redo_action)

        # IMPORTANT page 200
        # MAC OS uses a global menu barr so if you have multiple windows you'll want to create a menu bar for each one
        # it will also not display empty submenus
        # you can force it act like windows by using self.menuBar().setNativeMenuBar(False)
        # but this will be uncomfortable or even annoying for mac users

        toolbar = self.addToolBar("File")
        toolbar.addAction(open_action)
        # toolbar.addAction(save_action) # we changed how we added it down below

        # to disable being able to move the toolbar
        toolbar.setMovable(False)
        # floatable is whether it can be dragged to become an independent window
        toolbar.setFloatable(False)
        # if you comment out movable and floatable now you can drag it to the top or bottom areas only
        toolbar.setAllowedAreas(qtc.Qt.TopToolBarArea | qtc.Qt.BottomToolBarArea)

        # normally tool bars are icons and not text so let's change that
        open_icon = self.style().standardIcon(qtw.QStyle.SP_DirOpenIcon)
        save_icon = self.style().standardIcon(qtw.QStyle.SP_DriveHDIcon)
        # notice by doing it this way there is no icon associated with it in the menu bar, just the tool bar
        # and the action is only associated with the toolbar save button not the menu bar one as well
        toolbar.addAction(save_icon, "Save", lambda: self.statusBar().showMessage("File Saved"))

        # now add the icons to the actions
        open_action.setIcon(open_icon)
        # save_action.setIcon(save_icon)
        # important! to synchronize actions across multiple containers
        # either explicitly create QAction objects or save the references return from addAction()
        # to make sure you're adding the same action objects in each case
        help_action = qtw.QAction(self.style().standardIcon(qtw.QStyle.SP_DialogHelpButton), 'Help', self, #  important to pass parent
                                  triggered = lambda: self.statusBar().showMessage('Sorry no help yet!'))
        toolbar.addAction(help_action)

        # you can have as many toolbars as you want
        toolbar2 = qtw.QToolBar("Edit")
        toolbar2.addAction('Copy', self.textEdit.copy) # only copies and cuts selected area btw
        toolbar2.addAction('Cut', self.textEdit.cut)
        toolbar2.addAction('Paste', self.textEdit.paste)
        # here we specifiy to add toolbar2 to the right side of the screen
        self.addToolBar(qtc.Qt.RightToolBarArea, toolbar2)

        # dock widgets are kind of like toolbars but they can contain any kind of widget
        # they sit between toolbar areas and the central widget
        # dock widgets can only hold one widget but that doesn't mean it can't be nested!
        dock = qtw.QDockWidget("Replace")
        self.addDockWidget(qtc.Qt.LeftDockWidgetArea, dock)
        # to add features like closed, floated, moved you set with dockwidget feature enums
        # this sets what features are available! since being closed is missing you can't close it
        dock.setFeatures(qtw.QDockWidget.DockWidgetMovable | qtw.QDockWidget.DockWidgetFloatable)

        replace_widget = qtw.QWidget()
        replace_widget.setLayout(qtw.QVBoxLayout())
        dock.setWidget(replace_widget)

        self.search_text_inp = qtw.QLineEdit(placeholderText="search")
        self.replace_text_inp = qtw.QLineEdit(placeholderText="replace with")
        self.search_and_replace_btn = qtw.QPushButton("Search and Replace", clicked= self.search_and_replace)
        replace_widget.layout().addWidget(self.search_text_inp)
        replace_widget.layout().addWidget(self.replace_text_inp)
        replace_widget.layout().addWidget(self.search_and_replace_btn)
        # add stretch can be called on a layout to add an expanding Qwidget that pushes the other widgets together
        # kinda like using a spacer in QT designer
        replace_widget.layout().addStretch()

        help_menu.addAction('About', self.showAboutDialog)

        # a simple blocking question, if you say yes it does run the show command
        # response = qtw.QMessageBox.question(self, "My Text Editor", "This is a beta software, do you want to continue?"
        #                                     )
        # if response == qtw.QMessageBox.No:
        #     self.close()
        #     sys.exit()
        # here we're changing which buttons are available instead of the default yes or no
        # response = qtw.QMessageBox.question(self, "My Text Editor", "This is a beta software, do you want to continue?", qtw.QMessageBox.Yes | qtw.QMessageBox.Abort)
        # if response == qtw.QMessageBox.Abort:
        #     self.close()
        #     sys.exit()

        # and now here we're creating a custom dialog
        # alternatively if you want to create your own custom qmessage box you can do so
        splash_screen = qtw.QMessageBox()
        splash_screen.setWindowTitle("My Text Editor")
        # this is the main text displayed
        splash_screen.setText("BETA SOFTWARE WARNING!")
        # this is the detailed text under the main text
        splash_screen.setInformativeText("This is very, very beta, are you really sure you want to use it?")
        # this is the additional details text (which automatically adds a button details button)
        splash_screen.setDetailedText('This editor was written for pedagogical purposes, and probably is not fit for real work')
        # whether it is a modal or not requires an appropriate enum
        splash_screen.setWindowModality(qtc.Qt.WindowModal)
        # you can add as many buttons as you want
        splash_screen.addButton(qtw.QMessageBox.Yes)
        splash_screen.addButton(qtw.QMessageBox.Abort)
        # this is kind of confusing but basically translates to whether the dialog was accepted or rejected
        # https://doc.qt.io/qt-5/qdialog.html#result
        response = splash_screen.exec()
        if response == qtw.QMessageBox.Abort:
            self.close()
            sys.exit()
        # connecting the save and open file functions
        open_action.triggered.connect(self.openFile)
        save_action.triggered.connect(self.saveFile)

        edit_menu.addAction('Set Font…', self.set_font)

        edit_menu.addAction('Settings…', self.show_settings)

        # End main UI Code
        self.show()


    def search_and_replace(self):
        s_text = self.search_text_inp.text()
        r_text = self.replace_text_inp.text()
        if s_text:
            self.textEdit.setText(self.textEdit.toPlainText().replace(s_text, r_text))

    def showAboutDialog(self):
        # about is modaless which means it doesn't block
        # things like critical() does block!, try it by replacing about with critical
        qtw.QMessageBox.about(self, "About text_editor.py", "This is a text editor written in PyQt5.")
        # qtw.QMessageBox.critical(self, "About text_editor.py", "This is a text editor written in PyQt5.")

    def openFile(self):
        # why this weird syntax?
        # getOpenFileName() returns the filename selected and selected file type filter
        # you get 6 configuration categories in order
        # 1. the parent widget,
        # 2. the caption used in window title
        # 3. the starting directory as a path string
        # 4. the filters available for the file type filter dropdown
        # 5. the default selected filter
        # 6. option flags
        filename, _ = qtw.QFileDialog.getOpenFileName(self,
                                                      "Select a text file to open...",
                                                      qtc.QDir.homePath(),
                                                      'Text Files (*.txt) ;;Python Files (*.py) ;; All Files (*)',
                                                      'Python Files (*.py)',
                                                      # these two options are set by default,
                                                      # but they're here as an example
                                                      qtw.QFileDialog.DontUseNativeDialog |
                                                      qtw.QFileDialog.DontResolveSymlinks
                                                      )
        if filename:
            try:
                with open(filename, 'r') as fh:
                    self.textEdit.setText(fh.read())
            except Exception as e:
                qtw.QMessageBox.critical(f'Could not load file: {e}')


    def saveFile(self):
        # you could create your own QfileDialog option but why you would you?
        filename, _ = qtw.QFileDialog.getSaveFileName(self,
                                                      "Select the file to save to...",
                                                      qtc.QDir.homePath(),
                                                      'Text Files (*.txt) ;;Python Files (*.py) ;; All Files (*)'
                                                      )
        if filename:
            try:
                with open(filename, 'w') as fh:
                    fh.write(self.textEdit.toPlainText())
            except Exception as e:
                qtw.QMessageBox.critical(f'Could not load file: {e}')


    def set_font(self):
        current = self.textEdit.currentFont()
        # font, accepted = qtw.QFontDialog.getFont(current, self) #this grabs the font if possible
        font, accepted = qtw.QFontDialog.getFont(current, self, options = (
            qtw.QFontDialog.DontUseNativeDialog | # forces the use of the QT font selector
            qtw.QFontDialog.MonospacedFonts
        ))
        # and if accepted then update the current text font with the new font
        # the accepted is really a boolean of whether they hit yes or no
        # the font is returned as a QFont object
        # which returns the font family, style, size, effects and writing system of the font
        if accepted:
            self.textEdit.setCurrentFont(font)

class SettingsDialog(qtw.QDialog):
    """Dialog for setting the settings"""

    # notice this is similar to making your own custom widget/window
    # but with QDialog you get a few things for "free"
    # such as the self.accept and self.reject functions
    # and also an exec() function which tells us whether the dialog box was accepted or rejected
    def __init__(self, settings, parent = None):
        super().__init__(parent, modal = True) #remember modal is whether it blocks or not, in this case it does
        self.setLayout(qtw.QFormLayout())
        self.settings = settings #save our settings object to the class specific setting variable
        self.layout().addRow(qtw.QLabel('<h1>Application Settings</h1>'),)
        #old method
        #self.show_warnings_cb = qtw.QCheckBox(checked = settings.get('show_warnings'))
        # here it pulls from our saved settings to see whether to leave it checked or not
        # it cannot tell what the type of the data saved is so on retrieval, you must pass in a type as well
        self.show_warnings_cb = qtw.QCheckBox(checked = settings.value('show_warnings', type=bool))
        self.layout().addRow("Show Warnings", self.show_warnings_cb)

        self.accept_btn = qtw.QPushButton('Ok', clicked = self.accept)
        self.cancel_btn = qtw.QPushButton("Cancel", clicked = self.reject)
        self.layout().addRow(self.accept_btn, self.cancel_btn)

    # since we're passing in a mutable dict object we need to adjust the accept a little
    def accept(self):
        # old
        # self.settings['show_warnings'] = self.show_warnings_cb.isChecked()
        # update the settings file object thing with the new setting status
        self.settings.setValue('show_warnings', self.show_warnings_cb.isChecked())
        # then call the super method of the original accept for all the extra behind the scenes thigns
        super().accept()

if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    # app.setStyle("Fusion")
    # another dark theme
    # # Now use a palette to switch to dark colors:
    # palette = QPalette()
    # palette.setColor(QPalette.Window, QColor(53, 53, 53))
    # palette.setColor(QPalette.WindowText, qtc.Qt.white)
    # palette.setColor(QPalette.Base, QColor(25, 25, 25))
    # palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    # palette.setColor(QPalette.ToolTipBase, qtc.Qt.black)
    # palette.setColor(QPalette.ToolTipText, qtc.Qt.white)
    # palette.setColor(QPalette.Text, qtc.Qt.white)
    # palette.setColor(QPalette.Button, QColor(53, 53, 53))
    # palette.setColor(QPalette.ButtonText,qtc.Qt.white)
    # palette.setColor(QPalette.BrightText, qtc.Qt.red)
    # palette.setColor(QPalette.Link, QColor(42, 130, 218))
    # palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    # palette.setColor(QPalette.HighlightedText, qtc.Qt.black)
    # app.setPalette(palette)


    # # a dark theme preset, not bad i suppose
    # app.setStyle("Fusion")
    # dark_palette = QPalette()
    # dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    # dark_palette.setColor(QPalette.WindowText, qtc.Qt.white)
    # dark_palette.setColor(QPalette.Base, QColor(35, 35, 35))
    # dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    # dark_palette.setColor(QPalette.ToolTipBase, QColor(25, 25, 25))
    # dark_palette.setColor(QPalette.ToolTipText, qtc.Qt.white)
    # dark_palette.setColor(QPalette.Text, qtc.Qt.white)
    # dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    # dark_palette.setColor(QPalette.ButtonText, qtc.Qt.white)
    # dark_palette.setColor(QPalette.BrightText, qtc.Qt.red)
    # dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    # dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    # dark_palette.setColor(QPalette.HighlightedText, QColor(35, 35, 35))
    # dark_palette.setColor(QPalette.Active, QPalette.Button, QColor(53, 53, 53))
    # dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, qtc.Qt.darkGray)
    # dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, qtc.Qt.darkGray)
    # dark_palette.setColor(QPalette.Disabled, QPalette.Text, qtc.Qt.darkGray)
    # dark_palette.setColor(QPalette.Disabled, QPalette.Light, QColor(53, 53, 53))
    # app.setPalette(dark_palette)
    
    
    sys.exit(app.exec())
