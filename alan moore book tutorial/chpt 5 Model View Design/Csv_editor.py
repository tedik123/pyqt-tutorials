import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
import csv


# our custom model for the csv table
class CsvTableModel(qtc.QAbstractTableModel):

    def __init__(self, csv_file):
        super().__init__()
        self.filename = csv_file
        with open(self.filename) as fh:
            csvreader = csv.reader(fh)  # this reads it directly into memory so not great for large files
            self._headers = next(csvreader)  # assume the first row is the headers; grabbed by the next function
            self._data = list(csvreader)  # and then shove the rest of the rows in the _data property

    # both functions are required to take in a parent but it's not needed since there is no hierarchy for us
    def rowCount(self, parent):
        return len(self._data)

    def columnCount(self, parent):
        return len(self._headers)

    # the purpose of data function is to return the data in a single cell of the table
    # given the arguments of index and role
    # index is an instance of the QmodelIndex class,
    # which describes the location of a single node in a list, table or tree
    # every qmodel index contains the following properties:
    # a row number, a column number, a parent model index
    # we only care about column and row, if we had hiearchy we'd care about parent (which would be the index of the parent node)
    # if it were just a list we'd only care about row
    # role is a constant from the QtCore.Qt.ItemDataRole enum
    # when a view requests data from the model it passes a role value which requires data to be returned with an appropriate context
    # such as an EditRole where the data returned should be editable
    # DecorationRole would be an icon for an appropriate cell
    # if there is no data for a particular role, return nothing
    def data(self, index, role):
        # old
        # if role == qtc.Qt.DisplayRole:  # so here we only care about data displayed not editable
        #     return self._data[index.row()][index.column()]
        # by changing it to this method the text won't disappear when you click to edit it
        # this is because originally we had it only display if it had display role
        # not it's if it's either display or edit
        if role in (qtc.Qt.DisplayRole, qtc.Qt.EditRole):
            return self._data[index.row()][index.column()]

    # header data returns data on a single header given three pieces of information
    # I believe this means that if you click Cell C24 it will grab the header that belongs to the column C
    # section is an integer that indicates either the column number or row number (for vertical headers)
    # the role method is the context for which the data needs to be returned just like the data function
    def headerData(self, section, orientation, role):
        # headers can be horizontal or vertical
        if orientation == qtc.Qt.Horizontal and role == qtc.Qt.DisplayRole:
            return self._headers[section]
        return super().headerData(section, orientation, role)

    # in order for the data to be sortable we need to override the sort function
    # sort takes in a column number and order which can be DescendingOrder or AscendingOrder
    # TODO I don't quite understand how this works pg 245
    def sort(self, column, order):
        self.layoutAboutToBeChanged.emit()  # needs to be emitted before a sort, so they can be redrawn appropriately
        self._data.sort(key=lambda x: x[column])
        if order == qtc.Qt.DescendingOrder:
            self._data.reverse()
        self.layoutChanged.emit()  # needs to be emitted after a sort, so they can be redrawn appropriately

    # Qtcore.Qt.ItemFlag has a few flags such as can be :
    #   selected, dragged, dropped, checked, or edited
    def flags(self, index):
        # here we are passing in the ItemIsEditable flag, by default it's read only
        return super().flags(index) | qtc.Qt.ItemIsEditable  # this is a pipe operation not an OR btw

    # although are data can now be edited we must tell our model how to actually edit them
    # setData takes an index of the item to be set, the value to set it to, and an item role
    # it must return True if the task was successful and false otherwise
    # which we only want to do if
    def setData(self, index, value, role):
        if index.isValid() and role == qtc.Qt.EditRole:
            self._data[index.row()][index.column()] = value
            # if the data is changed it must emit the data changed signal
            # this signal is emitted whenever an item or a group is changed
            # top left most index, bottom-righmost index, and a list of the roles for each index
            # since we're only changing one cell we can pass the same index
            self.dataChanged.emit(index, index, [role])
            return True
        return False

    # row is where it starts, count is the amount of rows to be inserted
    # and the parent node is used for hierarchal data again
    # we must put the logic between beginInsert Rows and endInsertRows
    # where begin takes the ModelIndex of the parent node, in this case for tabular data it's just an empty QModelIndex
    # it also takes in the position where it will start and where it will end
    def insertRows(self, row, count, parent):
        self.beginInsertRows(parent or qtc.QModelIndex(),  # modelindex of parent
                             row,  # where start
                             row + count - 1)  # where end
        for i in range(count):   # here we generate a new row of equal length to the amount of headers
            default_row = [''] * len(self._headers)
            # then we insert a new row for the amount of counts we have
            self._data.insert(row, default_row)
        # then we have this obligatory call to endInsert Rows which i believe causes the redraw
        self.endInsertRows()

    def removeRows(self, position, rows, parent):
        # this is a tag to tell that you're starting a remove process
        self.beginRemoveRows(parent or qtc.QModelIndex(),  # this is basically the same call as insert rows
                             position,
                             position + rows - 1)
        for i in range(rows):
            del(self._data[position])
        # if you delete all of it you should insert an empty row
        if len(self._data) == 0:
            self.insertRows(1, 1, None)
        # the tag/redraw telling it that you're done manipulating the data
        self.endRemoveRows()

    # if you want to do column editing it's basically the same as remove rows

    def save_data(self):
        with open(self.filename, 'w', encoding='utf-8') as fh:
            writer = csv.writer(fh)
            writer.writerow(self._headers)
            # row(S) not row
            writer.writerows(self._data)




# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        self.tableview = qtw.QTableView()
        self.tableview.setSortingEnabled(True)
        self.setCentralWidget(self.tableview)

        self.model = None  # will add it in the select_file method

        menu = self.menuBar()
        file_menu = menu.addMenu('File')
        file_menu.addAction('Open', self.select_file)
        file_menu.addAction('Save', self.save_file)

        edit_menu = menu.addMenu('Edit')
        edit_menu.addAction('Insert Above', self.insert_above)
        edit_menu.addAction('Insert Below', self.insert_below)
        edit_menu.addAction('Remove Row(s)', self.remove_rows)



        # End main UI Code
        self.show()

    # get the user to pick a file
    def select_file(self):
        filename, _ = qtw.QFileDialog.getOpenFileName(self, 'Select a CSV file to open...', qtc.QDir.currentPath(),
                                                      'CSV Files (*.csv) ;; All Files (*)')
        if filename:
            self.model = CsvTableModel(filename)  # create the model from the csv file
            self.tableview.setModel(self.model)  # then add the model to the tableview


    # the model will save the file for us so we just need to check if the model exists
    # we have to create this wrapper method instead of attaching it to the menu bar because the model doesn't exist at
    # construction of main
    def save_file(self):
        if self.model:
            self.model.save_data()


    def insert_above(self):

        selected = self.tableview.selectedIndexes()
        row = selected[0].row()  # if selected else 0
        self.model.insertRows(row, 1, None)

    def insert_below(self):
        selected = self.tableview.selectedIndexes()
        row = selected[-1].row()  # if selected, else self.model.rowcount(none)
        self.model.insertRows(row + 1, 1, None)

    def remove_rows(self):
        selected = self.tableview.selectedIndexes()
        if selected:  # only delete if something is actually selected
            rows_to_delete = []
            [rows_to_delete.append(x.row()) for x in selected if x.row() not in rows_to_delete]
            # originally it would delete the amount of rows by the amount of elements selected
            # so you would have the entire row selected and it will delete rows equivalent in length
            # this checks so only unique rows are deleted
            self.model.removeRows(rows_to_delete[0], len(rows_to_delete), None)
            # self.model.removeRows(selected[0].row(), len(selected), None)




if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
