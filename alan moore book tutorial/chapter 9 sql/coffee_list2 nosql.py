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
        # Code starts here
        self.stack = qtw.QStackedWidget()
        self.setCentralWidget(self.stack)
        # Connect to the database
        db = qts.QSqlDatabase.addDatabase('QSQLITE')
        db.setDatabaseName('coffee.db')
        if not db.open():
            qtw.QMessageBox.critical(
                None, 'DB Connection Error',
                'Could not open database file: '
                f'{db.lastError().text()}')
            sys.exit(1)

        # Check for missing tables
        required_tables = {'roasts', 'coffees', 'reviews'}
        missing_tables = required_tables - set(db.tables())
        if missing_tables:
            qtw.QMessageBox.critical(
                None, 'DB Integrity Error',
                'Missing tables, please repair DB: '
                f'{missing_tables}')
            sys.exit(1)
        # Main UI Code goes here
        self.reviews_model = qts.QSqlTableModel()
        # grab the reviews table
        self.reviews_model.setTable('reviews')

        # we use relational because we know that there is a relationship between reviews
        # and coffees that we'll want tc combine
        self.coffees_model = qts.QSqlRelationalTableModel()
        # grab the coffees table
        self.coffees_model.setTable('coffees')
        # to combine the reviews and coffees we can set the relation to the roast_id
        # which the user doesn't care for and we'll replace with the roasts detailed information
        self.coffees_model.setRelation(self.coffees_model.fieldIndex('roast_id'),
                                       # the first is table name, the related column roast_id = id of roast,
                                       # and the field to display
                                       qts.QSqlRelation('roasts', 'id', 'description'))
        # so now we'll see description in place of the coffees roast_id

        # whenever we reconfigure an SQL table we must call select, this cauases the model to generate
        # and run an SQL query
        #         self.coffees_model.select() # moved down below
        # self.mapper.model().select()

        # IMPORTANT by default it is read/write! You can edit/destroy data!
        # create the table widget and set the model as our coffees model/sql link
        self.coffee_list = qtw.QTableView()
        self.coffee_list.setModel(self.coffees_model)
        # add to view
        self.stack.addWidget(self.coffee_list)
        self.coffees_model.select()

        toolbar = self.addToolBar('Controls')
        toolbar.addAction('Delete Coffee(s)', self.delete_coffee)
        toolbar.addAction('Add Coffee', self.add_coffee)

        # for things that are only categorial we should set it so the input matches
        # that's where delegates come in and we can use that as follows
        self.coffee_list.setItemDelegate(qts.QSqlRelationalDelegate())

        # now let's add the coffee form
        self.coffee_form = CoffeeForm(self.coffees_model, self.reviews_model)
        self.stack.addWidget(self.coffee_form)
        # this changes the mapper to widget/row selected
        self.coffee_list.doubleClicked.connect(self.coffee_form.show_coffee)
        # but then you have to change the current widget DISPLAYED with self.stack.setCurrentWidget(widget)
        self.coffee_list.doubleClicked.connect(lambda: self.stack.setCurrentWidget(self.coffee_form))

        toolbar.addAction("Back to list", self.show_list)

        # End main UI Code
        self.show()

    def delete_coffee(self):
        selected = self.coffee_list.selectedIndexes()
        for index in selected or []:
            self.coffees_model.removeRow(index.row())

    def add_coffee(self):
        self.stack.setCurrentWidget(self.coffee_list)
        self.coffees_model.insertRows(
            self.coffees_model.rowCount(), 1
        )

    def show_list(self):
        self.coffee_list.resizeColumnsToContents()
        self.coffee_list.resizeRowsToContents()
        self.stack.setCurrentWidget(self.coffee_list)


# let's implement a custom widget that will allows us to add dates in a better manner
class DateDelegate(qtw.QStyledItemDelegate):

    # createEditor is responsible for returning the widget that will be used for editing the data
    # IMPORTANT there's more you can do page 424- 425 elaborates
    def createEditor(self, parent, option, index):
        # if you don't pass in a parent it will create a new window
        date_inp = qtw.QDateEdit(parent, calendarPopup=True)
        return date_inp


class CoffeeForm(qtw.QWidget):
    def __init__(self, coffees_model, reviews_model):
        super().__init__()
        # Main UI Code goes here
        self.setLayout(qtw.QFormLayout())
        self.coffee_brand = qtw.QLineEdit()
        self.layout().addRow('Brand: ', self.coffee_brand)
        self.coffee_name = qtw.QLineEdit()
        self.layout().addRow('Name ', self.coffee_name)
        self.roast = qtw.QComboBox()
        self.layout().addRow('Roast: ', self.roast)

        self.coffees_model = coffees_model
        # the purpose of a mapper is to map fields from a model to widgets in a form
        # the mapper sits between the model and the form's fields translating the columns between them
        # in order to ensure the data is written properly
        self.mapper = qtw.QDataWidgetMapper(self)
        self.mapper.setModel(coffees_model)
        self.mapper.setItemDelegate(qts.QSqlRelationalDelegate(self))

        # now that we have a mapper we need to define the field mappings with addMapping()
        # here coffees model is the object containing our SQL database it's not quite an SQL database tho!
        # there is a difference, it's just an abstraction to make it easier to interact with SQL
        self.mapper.addMapping(
            self.coffee_brand,
            coffees_model.fieldIndex('coffee_brand')
        )
        # addMapping takes in widget and a model column number, we're using fieldIndex to make it easier
        # but if you knew the numbers you can just plug that in instead
        self.mapper.addMapping(
            self.coffee_name,
            coffees_model.fieldIndex('coffee_name')
        )
        self.mapper.addMapping(
            self.roast,
            coffees_model.fieldIndex('description')
        )
        # now in order to populate our combobox of roasts we need to populate it
        # we can do that by using the roasts_model
        # normally we'd retreive it by roast_id but we replaced roast_id with description keep that in mind
        roasts_model = coffees_model.relationModel(
            coffees_model.fieldIndex('description')
        )
        self.roast.setModel(roasts_model)
        self.roast.setModelColumn(1)

        # now let's handle the reviews
        # we already have the model so we just need to add it a view
        self.reviews = qtw.QTableView()
        self.layout().addWidget(self.reviews)
        self.reviews.setModel(reviews_model)
        # we want to hide id (of the roast) and coffee_id because the user doesn't care about them
        self.reviews.hideColumn(0)
        self.reviews.hideColumn(1)
        # and then we'll stretch the review part as far to the right as we can
        self.reviews.horizontalHeader().setSectionResizeMode(4, qtw.QHeaderView.Stretch)

        # now to add our custom delegate to the table view
        self.dateDelegate = DateDelegate()
        # notice it won't error if the fieldIndex does not exist!!!
        self.reviews.setItemDelegateForColumn(
            reviews_model.fieldIndex('review_date'),
            self.dateDelegate
        )

        # now let's allow for editing for reviews/adding and such
        self.new_review = qtw.QPushButton('New Review', clicked = self.add_review)
        # pretty sure this will error
        self.delete_review = qtw.QPushButton('Delete Review', clicked = self.delete_review)
        self.layout().addRow(self.new_review, self.delete_review)

    # deleting is pretty simple just delete at index
    def delete_review(self):
        for index in self.reviews.selectedIndexes() or []:
            self.reviews.model().removeRow(index.row())
        self.reviews.model().select()

    # to add rows we need to make sure we're adding to the current coffee_id's reviews not all coffees/reviews
    def add_review(self):
        reviews_model = self.reviews.model()
        # this is grabbing the formatting of the model
        new_row = reviews_model.record()
        # notice we left id out because by default if it's null it will create one for us in the backend
        defaults = {
            'coffee_id': self.coffee_id,
            'review_date': qtc.QDate.currentDate(),
            'reviewer': "",
            'review': ""
        }
        # this is just setting the defaults to be displayed on the sheet
        for field, value in defaults.items():
            index = reviews_model.fieldIndex(field)
            new_row.setValue(index, value)

        # now we need to actually insert it into the model?
        inserted = reviews_model.insertRecord(-1, new_row)
        if not inserted:
            error = reviews_model.lastError().text()
            print(f'Insert Failed: {error}')
        reviews_model.select()

    # our coffee list can display all records but we want our coffee form to only show one at a time
    # that's why the mapper has the concept of current widgets/records
    # we just need to control how it should navigate through the table
    # we have toFirst(), toLast(), toNext(), toPrevious(), setCurrentIndex()
    # since our user is picking an uknown one we want to use setCurrentIndex()
    # this is not the same as the coffees id value,
    # it's stricly the model row number to pick the selected row correctly!
    def show_coffee(self, coffee_index):
        self.mapper.setCurrentIndex(coffee_index.row())
        # as of right now it will display all the reviews of all coffees regardless of which one you select
        # so we need to filter
        id_index = coffee_index.siblingAtColumn(0)
        self.coffee_id = int(self.coffees_model.data(id_index))
        # you have to use strings here so be careful with input it is a security issue and things can be injected
        # by setting it to an int we somewhat offset that risk
        self.reviews.model().setFilter(f'coffee_id = {self.coffee_id}')
        self.reviews.model().setSort(3, qtc.Qt.DescendingOrder)
        # select updates the model
        self.reviews.model().select()
        # resize so it looks better
        self.reviews.resizeRowsToContents()
        self.reviews.resizeColumnsToContents()


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    mw.setMinimumSize(425, 250)
    sys.exit(app.exec())
