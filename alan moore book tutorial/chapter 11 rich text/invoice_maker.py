import sys

from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc
from PyQt5 import QtMultimedia as qtmm
from PyQt5 import QtPrintSupport as qtps

# IMPORTANT if you get stuck
# https://github.com/packtpublishing/mastering-gui-programming-with-python
# idk how helpful this is but:
# https://doc.bccnsoft.com/docs/PyQt5/pyqt4_differences.html#pyuic5
class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here

        main = qtw.QWidget()
        main.setLayout(qtw.QHBoxLayout())
        self.setCentralWidget(main)

        form = InvoiceForm()
        main.layout().addWidget(form)

        self.preview = InvoiceView()
        main.layout().addWidget(self.preview)

        form.submitted.connect(self.preview.build_invoice)

        # toolbar menu
        print_tb = self.addToolBar('Printing')
        print_tb.addAction('Configure Printer', self.printer_config)
        print_tb.addAction('Print Preview', self.print_dialog)
        print_tb.addAction('Export PDF', self.export_pdf)

        # actual printer setup
        self.printer = qtps.QPrinter()
        self.printer.setOrientation(qtps.QPrinter.Portrait)
        self.printer.setPageSize(qtg.QPageSize(qtg.QPageSize.Letter))

        # End main UI Code
        self.show()

    # this is to take in inputs from the user on how they want it printed
    # typically this uses the OS dialog
    def printer_config(self):
        # this automaticallly adds all the settings to the printer as the user makes changes
        dialog = qtps.QPageSetupDialog(self.printer, self)
        dialog.exec()
    #   since printer object is not a Qobject there are no signals we need to update at the end manually
        self._update_preview_size()

    # this just updates the preview to reflect the user changes after printer_config
    def _update_preview_size(self):
        # updating the page preview with the rect
        # but we pass in points
        # a point is 1/72 of an inch (real dimensions)
        self.preview.set_page_size(
            self.printer.pageRect(qtps.QPrinter.Point)
        )

    def _print_document(self):
        # this is how we load the document into the printer
        # kind of in a reverse syntax?
        self.preview.document().print(self.printer)


    # this will actually do the printing via OS
    def print_dialog(self):
        self._print_document()
        # pass in the printer that already contains the document
        # and the OS will take over from here
        dialog = qtps.QPrintDialog(self.printer, self)
        # if you don't want to block you can use .open() instead, but there are some race conditions that may cause
        # this to fail
        dialog.exec()
        self._update_preview_size()

    def print_preview(self):
        dialog = qtps.QPrintPreviewDialog(self.printer, self)
        # requesting it repaints/up to date with the settings
        # connecting it to our _print_document which passes in the changed version of the document to the printer
        dialog.paintRequested(self._print_document())
        dialog.exec()
        self._update_preview_size()

    def export_pdf(self):
        filename, _ = qtw.QFileDialog.getSaveFileName(
            self, "Save to PDF", qtc.QDir.currentPath(), "PDF Files (*.pdf)"
        )
        if filename:
            self.printer.setOutputFileName(filename)
            self.printer.setOutputFormat(qtps.QPrinter.PdfFormat)
            self._print_document()

class InvoiceForm(qtw.QWidget):
    submitted = qtc.pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setLayout(qtw.QFormLayout())
        self.inputs = dict()
        self.inputs["Customer Name"] = qtw.QLineEdit()
        self.inputs["Customer Address"] = qtw.QPlainTextEdit()
        self.inputs["Invoice Date"] = qtw.QDateEdit(
            date=qtc.QDate.currentDate(), calendarPopup=True)
        self.inputs['Days until Due'] = qtw.QSpinBox(
            minimum=0, maximum=60, value=30
        )
        for label, widget in self.inputs.items():
            self.layout().addRow(label, widget)
        self.line_items = qtw.QTableWidget(rowCount=10, columnCount=3)
        self.line_items.setHorizontalHeaderLabels(
            ['Job', "Rate", 'Hours']
        )
        self.line_items.horizontalHeader().setSectionResizeMode(qtw.QHeaderView.Stretch)
        self.layout().addRow(self.line_items)
        for row in range(self.line_items.rowCount()):
            for col in range(self.line_items.columnCount()):
                if col > 0:
                    # the last two columns are numbers so we want to replace the default lineEdit with a spin box
                    w = qtw.QSpinBox(minimum=0)
                    self.line_items.setCellWidget(row, col, w)
        submit = qtw.QPushButton("Create Invoice", clicked=self.on_submit)
        self.layout().addRow(submit)

    def on_submit(self):
        # this extacts all the relevent data into our dict
        data = {'c_name': self.inputs['Customer Name'].text(), 'c_addr': self.inputs['Customer Address'].toPlainText(),
                'i_date': self.inputs['Invoice Date'].date().toString(),
                'i_due': self.inputs['Invoice Date'].date().addDays(
                    self.inputs['Days until Due'].value()).toString(),
                'i_terms': '{} days'.format(self.inputs['Days until Due'].value()), 'line_items': list()}
        for row in range(self.line_items.rowCount()):
            # for every row that has a description
            if not self.line_items.item(row, 0):
                continue
            job = self.line_items.item(row, 0).text()
            rate = self.line_items.cellWidget(row, 1).value()
            hours = self.line_items.cellWidget(row, 2).value()
            total = rate * hours
            row_data = [job, rate, hours, total]
            if any(row_data):
                data['line_items'].append(row_data)
        # get the sum of all jobs
        # the 4th position is where our total is in
        data['total_due'] = sum(x[3] for x in data['line_items'])
        self.submitted.emit(data)


class InvoiceView(qtw.QTextEdit):
    dpi = 72
    # this is so they're aligned with the standard US letter size
    doc_width = 8.5 * dpi
    doc_height = 11 * dpi

    def __init__(self):
        super().__init__(readOnly=True)
        self.setFixedSize(qtc.QSize(self.doc_width, self.doc_height))

    def build_invoice(self, data):
        document = qtg.QTextDocument()
        # fyi qtextedit view has it's own document we could use
        # but we want to start fresh
        self.setDocument(document)
        document.setPageSize((qtc.QSizeF(self.doc_width, self.doc_height)))
        # documents have a bit of a strange syntax so pay attention carefully
        # you have a cursor you need to place to start
        cursor = qtg.QTextCursor(document)
        cursor.insertText("Invoice, woohoo")
        # a QTextDocument is made up of multiple parts: frames, blocks, and fragments
        # frame is a QTextFrame object it is a rectangular region that can contain any type of content including
        # other frames
        # Blocks are QTextBlock objects, a region text surrounded by line breaks such as a paragraph or list item
        # a fragment is a QTextFragment object, it is a contiguous region of text inside a
        # block that shares a common text formatting, so you can have fragments combined in one block
        # but with different formatting for each fragment
        # the root is the rootFrame on all QTextDocuments
        # we'll use this to return the cursor to the beginning
        root = document.rootFrame()

        cursor.setPosition((root.lastPosition()))
        #       first frame format and then insert to create it
        logo_frame_fmt = qtg.QTextFrameFormat()
        logo_frame_fmt.setBorder(2)
        logo_frame_fmt.setPadding(10)
        # insert returns QTextFrame object created
        logo_frame = cursor.insertFrame(logo_frame_fmt)

        # since we don't want to add stuff to the logo frame we return to root
        cursor.setPosition(root.lastPosition())
        cust_addr_frame_fmt = qtg.QTextFrameFormat()
        cust_addr_frame_fmt.setWidth(self.doc_width * .3)
        # floating means it will be pushed to the right and other content will flow around it
        cust_addr_frame_fmt.setPosition(qtg.QTextFrameFormat.FloatRight)
        cust_addr_frame = cursor.insertFrame(cust_addr_frame_fmt)

        #       terms frame
        #       there's a QT quirk here and it will set this frame one line below where the customer frame starts
        #        to fix this you can use a table to format it exactly evenly
        cursor.setPosition(root.lastPosition())
        terms_frame_fmt = qtg.QTextFrameFormat()
        terms_frame_fmt.setWidth(self.doc_width * .5)
        terms_frame_fmt.setPosition(qtg.QTextFrameFormat.FloatLeft)
        terms_frame = cursor.insertFrame(terms_frame_fmt)

        # note we don't need to do any formatting just create the textFrame every time
        # but if you do you have to do it before inserting it!
        # you can also reuse frame formats if you need to!
        cursor.setPosition(root.lastPosition())
        line_items_frame_fmt = qtg.QTextFrameFormat()
        line_items_frame_fmt.setMargin(25)
        line_items_frame = cursor.insertFrame(line_items_frame_fmt)

        # within frames you need to define a character format
        # we'll use these a bit later when adding text
        std_format = qtg.QTextCharFormat()
        logo_format = qtg.QTextCharFormat()
        logo_format.setFont(qtg.QFont('Impact', 24, qtg.QFont.DemiBold))
        logo_format.setUnderlineStyle(qtg.QTextCharFormat.SingleUnderline)
        logo_format.setVerticalAlignment(qtg.QTextCharFormat.AlignMiddle)

        label_format = qtg.QTextCharFormat()
        label_format.setFont(qtg.QFont('Sans', 12, qtg.QFont.Bold))

        # call this to get the beginning of the frame
        cursor.setPosition(logo_frame.firstPosition())
        #       you could insert an image like this but it allows for no formatting
        #         cursor.insertImage('nc_logo.png')
        logo_img_fmt = qtg.QTextImageFormat()
        logo_img_fmt.setName('nc_logo.png')
        logo_img_fmt.setHeight(48)
        cursor.insertImage(logo_img_fmt, qtg.QTextFrameFormat.FloatLeft)
        # this is adding the company information at the top
        cursor.insertText('   ')
        cursor.insertText('Ninja Coders, LLC', logo_format)
        cursor.insertBlock()
        cursor.insertText('  123 N Wizard St. Yonkers, NY 10701', std_format)

        # customer information
        cursor.setPosition(cust_addr_frame.lastPosition())
        address_format = qtg.QTextBlockFormat()
        address_format.setAlignment(qtc.Qt.AlignRight)
        address_format.setRightMargin(25)
        address_format.setLineHeight(
            # the second argument is how the height should be interpreted
            # proportional is a % of the line height
            # in this case it's 150%
            150, qtg.QTextBlockFormat.ProportionalHeight
        )
        #       let's actually insert
        #       each time we insert a block it's like inserting a new paragraph
        cursor.insertBlock(address_format)
        cursor.insertText('Customer:', label_format)
        cursor.insertBlock(address_format)
        cursor.insertText(data['c_name'], std_format)
        cursor.insertBlock(address_format)
        cursor.insertText(data['c_addr'])

        cursor.setPosition(terms_frame.lastPosition())
        cursor.insertText('Terms:', label_format)
        # can be a constant or a QTextListFormat object
        cursor.insertList(qtg.QTextListFormat.ListDisc)

        term_items = {
            f'<b>Invoice dated: </b> {data["i_date"]}',
            f'<b>Invoice terms: </b> {data["i_terms"]}',
            f'<b>Invoice due: </b> {data["i_due"]}'
        }
        for i, item in enumerate(term_items):
            # this is so we don't insert a block in the first bullet point
            if i > 0:
                cursor.insertBlock()
            # since we used rich text we need to say insertHtml not insertText
            # it also does not accept an additional formatting argument like insertText does
            cursor.insertHtml(item)

        #       finally we'll insert a table for our line items
        table_format = qtg.QTextTableFormat()
        # we'll basically be using this to say
        # is that the first row is the header row and should be repeated on each page
        table_format.setHeaderRowCount(1)
        table_format.setWidth(
            qtg.QTextLength(qtg.QTextLength.PercentageLength, 100)
        )
        headings = ('Job', 'Rate', 'Hours', 'Cost')
        # calculating rows and columns dependent on our headings
        num_rows = len(data['line_items']) + 1
        num_cols = len(headings)
        cursor.setPosition(line_items_frame.lastPosition())
        table = cursor.insertTable(num_rows, num_cols, table_format)
        for heading in headings:
            cursor.insertText(heading, label_format)
            # there's A LOT of positions you could use
            cursor.movePosition(qtg.QTextCursor.NextCell)
        for row in data['line_items']:
            for col, value in enumerate(row):
                # if it's in the second or 4th column we need to add a $ sign
                text = f'${value}' if col in (1, 3) else f'{value}'
                cursor.insertText(text, std_format)
                cursor.movePosition(qtg.QTextCursor.NextCell)
        table.appendRows(1)
        cursor = table.cellAt(num_rows, 0).lastCursorPosition()
        cursor.insertText('Total', label_format)
        cursor = table.cellAt(num_rows, 3).lastCursorPosition()
        cursor.insertText(f"${data['total_due']}", label_format)

    # via an inputed rectangle dimensions we'll change the document size
    def set_page_size(self, qrect):
        self.doc_width = qrect.width()
        self.doc_height = qrect.height()
        self.setFixedSize(qtc.QSize(self.doc_width, self.doc_height))
        self.document().setPageSize(
            qtc.QSizeF(self.doc_width, self.doc_height))


if __name__ == '__main__':
    app = qtw.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec())
