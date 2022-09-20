from PyQt5 import QtWidgets as qtw
from PyQt5 import QtGui as qtg
from PyQt5 import QtCore as qtc

# by doing relative imports you can gurantee that you'll import from this container instead of from the system
# which might have a package with the same name
from .engine import TicTacToeEngine
from .board import TTTBoard


class MainWindow(qtw.QMainWindow):
    def __init__(self):
        super().__init__()
        # Main UI Code goes here
        self.board = TTTBoard()
        self.board_view = qtw.QGraphicsView()
        self.board_view.setScene(self.board)
        self.setCentralWidget(self.board_view)
        self.board.square_clicked.connect(self.try_mark)

        self.start_game()
        # End main UI Code
        self.show()

    def start_game(self):
        self.board.clear_board()
        self.game = TicTacToeEngine()
        self.game.game_won.connect(self.game_won)
        self.game.game_draw.connect(self.game_draw)

    def try_mark(self, square):
        if self.game.mark_square(square):
            self.board.set_board(self.game.board)
            self.game.check_board()

    def game_won(self, player):
        """Display the winner and start a new game"""
        qtw.QMessageBox.information(None, 'Game Won', f'Player {player} Won!')
        self.start_game()

    def game_draw(self):
        """Display the lack of a winner and start a new game"""
        qtw.QMessageBox.information(None, 'Game Draw', 'Nobody won...')
        self.start_game()
