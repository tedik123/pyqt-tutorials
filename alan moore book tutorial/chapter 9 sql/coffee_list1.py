import os
import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from PyQt5 import QtSql as qts


# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        # remember stacked widget is like a tab widget but without tabs, it switches screens between things
        self.stack = qtw.QStackedWidget()
        self.setCentralWidget(self.stack)

        # let's create the database connection
        # QSQLITE is the name of the driver we want to use not the actual database name
        self.db = qts.QSqlDatabase.addDatabase('QSQLITE')
        # then we'd input a password if needed but we don't so let's just connect directly to our db
        # IMPORTANT you need to convert your SQL file to a db file by using the command:
        #  sqlite3 file.db -init file.sql
        #  very important!!!!
        self.db.setDatabaseName('coffee.db')

        if not self.db.open():
            error = self.db.lastError().text()
            qtw.QMessageBox.critical(None, 'DB Connection Error', f'Could not open database file: {error}')
            sys.exit(1)
        print(self.db.database())
        # now we are connected with self.db.open()
        # let's see if we can read all the tables
        required_tables = {'roasts', 'coffees', 'reviews'}
        tables = self.db.tables()
        print(tables)
        missing_tables = required_tables - set(tables)
        if missing_tables:
            qtw.QMessageBox.critical(None, 'DB Integrity Error',
                                     'Missing Tables please repair DB: ' f'{missing_tables}')
            sys.exit(1)

        #                    this converts our string into an SQL command
        # and returns the result
        query = self.db.exec('SELECT count(*) FROM coffees')
        # to retrieve the data
        # why next?
        # there's a cursor that is pointed at nothign to begin
        # so you must move it to the next row for it to point to the first row
        query.next()
        # query value(0) returns the first column of that row value(1) would return the second and so on
        count = query.value(0)
        print(f'There are {count} coffees in the database.')
        # if there are no more valuesf query.next() returns False
        query = self.db.exec('SELECT * FROM roasts order by id')
        roasts = []
        while query.next():
            roasts.append(query.value(1))
        print(f'roasts : {roasts}')
        # now that we have our roasts we can create the form
        self.coffee_form = CoffeeForm(roasts)
        self.stack.addWidget(self.coffee_form)

        # let's use QTSQL to format for us
        # again don't need to pass in a database since there's only 1
        # this will create a tablemodel
        coffees = qts.QSqlQueryModel()
        coffees.setQuery("SELECT id, coffee_brand, coffee_name AS coffee "
                         "FROM coffees ORDER BY id")
        print(coffees)
        self.coffee_list = qtw.QTableView()
        self.coffee_list.setModel(coffees)
        self.stack.addWidget(self.coffee_list)
        self.stack.setCurrentWidget(self.coffee_list)
        # by default it will use the sql headers we have but we can override it like this
        # keep in mind you can't edit SQL data from pyqt while using SQL
        coffees.setHeaderData(1, qtc.Qt.Horizontal, 'Brand')
        coffees.setHeaderData(2, qtc.Qt.Horizontal, 'Product')


        # let's create a navigation bar
        navigation = self.addToolBar('Navigation')
        navigation.addAction('Back to list',
                             lambda: self.stack.setCurrentWidget(self.coffee_list))

        self.coffee_list.doubleClicked.connect(lambda x: self.show_coffee(self.get_id_for_row(x)))

        # End main UI Code
        self.show()

    # we need this because the list widget double click returns an index but we need a coffee id instead
    # so this will translate the index to a coffee id
    def get_id_for_row(self, index):
        # this retrives the first column of the one you clicked, which in this case is our id
        index = index.siblingAtColumn(0)
        print(index)
        coffee_id = self.coffee_list.model().data(index)
        print(coffee_id)
        return coffee_id

    def show_coffee(self, coffee_id):
        # this is bad because you can put in anything for id like {0; DELETE FROM coffees}
        # which would delete everything
        # query = self.db.exec(f'SELECT * FROM coffees WHERE id= {coffee_id}')
        # a better way to this is
        query1 = qts.QSqlQuery(self.db)
        query1.prepare('SELECT * FROM coffees WHERE id=:id')
        query1.bindValue(':id', coffee_id)
        # here we actually bind the value to id so you can't pass in whatever you want
        query1.exec()
        # then extraction
        query1.next()
        coffee = {
            'id': query1.value(0),
            'coffee_brand': query1.value(1),
            'coffee_name': query1.value(2),
            'roast_id': query1.value(3)
        }
        # notice we didn't pass in the database because there's only one that we've already connected to
        # if we had multiple we'd need to switch between them to ensure we're using the right one
        query2 = qts.QSqlQuery()
        query2.prepare('SELECT * FROM reviews WHERE coffee_id=:id')
        query2.bindValue(':id', coffee_id)
        query2.exec()
        reviews = []
        while query2.next():
            reviews.append((
                # here instead of using numbers we're using the column header names
                query2.value('reviewer'),
                query2.value('review_data'),
                query2.value('review')
            ))

        self.coffee_form.show_coffee(coffee, reviews)
        self.stack.setCurrentWidget(self.coffee_form)
        # return coffee

class CoffeeForm(qtw.QWidget):
    def __init__(self, roasts):
        super().__init__()
        # Main UI Code goes here
        self.setLayout(qtw.QFormLayout())
        self.coffee_brand = qtw.QLineEdit()
        self.layout().addRow('Brand: ', self.coffee_brand)
        self.coffee_name = qtw.QLineEdit()
        self.roast = qtw.QComboBox()
        self.roast.addItems(roasts)
        self.layout().addRow('Roast: ', self.roast)
        self.reviews = qtw.QTableWidget(columnCount=3)
        self.reviews.horizontalHeader().setSectionResizeMode(2, qtw.QHeaderView.Stretch)
        self.layout().addRow(self.reviews)

    # assumes coffee_data is a dict object?
    def show_coffee(self, coffee_data, reviews):
        self.coffee_brand.setText(coffee_data.get('coffee_brand'))
        self.coffee_name.setText(coffee_data.get('coffee_name'))
        self.roast.setCurrentIndex(coffee_data.get('roast_id'))
        self.reviews.clear()
        self.reviews.setHorizontalHeaderLabels(['Reviewer', 'Date', 'Review'])
        self.reviews.setRowCount(len(reviews))
        for i, review in enumerate(reviews):
            for j, value in enumerate(review):
                self.reviews.setItem(i, j, qtw.QTableWidgetItem(value))


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
