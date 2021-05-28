from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtWidgets, uic, QtCore
import sys
from functools import partial
import random
import sprites  # loads spritesheet.png file
from pprint import pprint as print
import json
import datetime

JSON_FILE: str = "data.json"
JSON_CONTENTS = None


class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("form.ui", self)
        self.setStyleSheet(open("style.qss", "r").read())
        self.setWindowIcon(QIcon("icon.png"))
        if JSON_CONTENTS["settings"][0]["ShowTut"][0] == "True":
            self.actionShow_Tutorial.setChecked(True)
            QMessageBox.information(
                self,
                "How to Play",
                "Make all the boxes blue to win!",
                QMessageBox.Ok,
                QMessageBox.Ok,
            )
        else:
            self.actionShow_Tutorial.setChecked(False)

        self.actionAsk_to_play_again_dialog.setChecked(
            JSON_CONTENTS["settings"][0]["Quick Play"][0] == "True"
        )
        self.actionAsk_to_play_again_dialog.triggered.connect(
            self.togglePlayAgainDialog
        )

        self.show_play_again_dialog = JSON_CONTENTS["settings"][0]["Quick Play"][0]

        self.actionShow_Tutorial.triggered.connect(self.toggleTutorial)

        self.action_Restart.triggered.connect(self.restart_game)

        self.grid_size_x: int = 4
        self.grid_size_y: int = 4
        self.button_size: int = 128
        self.font_size: int = 65
        self.use_images: bool = True

        self.saved_time: int = 0
        self.global_game_time: int = 0
        self.current_moves: int = 0

        # self.shortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        # self.shortcut.activated.connect(self.revert_move)

        self.restart_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        self.restart_shortcut.activated.connect(self.restart_game)

        self.curr_time: QTime = QtCore.QTime(00, 00, 00)
        self.game_time: QTime = QtCore.QTime(00, 00, 00)

        self.start_time = None
        self.end_time = None

        self.overall_start_time = None
        self.overall_end_time = None

        self.game_timer = QtCore.QTimer()
        self.game_timer.timeout.connect(self.update_game_time)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.time)

        self.pressed_first_button = False

        self.currently_played: int = 0
        self.game_limit: int = 10
        self.average_time: list = []
        self.average_score: list = []

        # self.timer.start(1000)
        self.setWindowTitle(f"Flip {self.currently_played}/{self.game_limit}")

        self.generate_board()
        self.showMaximized()
        self.show()
        self.update_grid_sizes()

    def restart_game(self):
        self.pressed_first_button = False
        self.average_time.clear()
        self.average_score.clear()
        self.curr_time = QtCore.QTime(00, 00, 00)
        self.game_time = QtCore.QTime(00, 00, 00)
        self.current_moves = 0
        self.saved_time = 0
        self.global_game_time = 0
        self.lblGameTime.setText(
            f"Game Time:\n{self.game_time.hour():02d}:{self.game_time.minute():02d}:{self.game_time.second():02d}"
        )
        self.timer.stop()
        self.currently_played: int = 0
        self.setWindowTitle(f"Flip {self.currently_played}/{self.game_limit}")
        self.generate_board()

    def togglePlayAgainDialog(self):
        JSON_CONTENTS["settings"][0]["Quick Play"][0] = str(
            self.actionAsk_to_play_again_dialog.isChecked()
        )
        with open(JSON_FILE, "w") as f:
            json.dump(JSON_CONTENTS, f, indent=4)

        self.show_play_again_dialog = self.actionAsk_to_play_again_dialog.isChecked()

    def toggleTutorial(self):
        JSON_CONTENTS["settings"][0]["ShowTut"][0] = str(
            self.actionShow_Tutorial.isChecked()
        )
        with open(JSON_FILE, "w") as f:
            json.dump(JSON_CONTENTS, f, indent=4)

    def update_grid_sizes(self):
        self.menuGrid_Size.clear()
        for i, grid_size in enumerate(JSON_CONTENTS["records"][0].keys()):
            x = int(grid_size.split("x")[0])
            y = int(grid_size.split("x")[1])
            grid = QAction(grid_size, self)
            try:
                record_time = int(
                    JSON_CONTENTS["records"][0][f"{grid_size}"][0]["Time"]
                )
                record_moves = int(
                    JSON_CONTENTS["records"][0][f"{grid_size}"][0]["Moves"]
                )
                grid.setStatusTip(
                    f"Record Time: {str(datetime.timedelta(seconds=record_time))}    Record Moves: {record_moves}"
                )
            except ValueError:
                grid.setStatusTip(f"Record Time: Undfined    Record Moves: Undfined")
            grid.triggered.connect(partial(self.set_quick_grid_size, y, x))
            self.menuGrid_Size.addAction(grid)

        self.setGridSize = QAction("Custom")
        self.setGridSize.triggered.connect(self.set_new_grid_size)
        self.menuGrid_Size.addAction(self.setGridSize)

    def set_quick_grid_size(self, x: int, y: int):
        self.grid_size_x = x
        self.grid_size_y = y
        self.generate_board()

    def set_new_grid_size(self):
        text, okPressed = QInputDialog.getText(
            self, "Grid Size", "Formula: X x Y. Etc 4x4 or 6x3.", QLineEdit.Normal, ""
        )
        if okPressed and text != "":
            text = text.replace(" ", "").split("x")
            self.grid_size_x = int(text[0])
            self.grid_size_y = int(text[1])
            self.generate_board()
        self.update_grid_sizes()

    def update_game_time(self):
        self.game_time = self.game_time.addSecs(1)
        self.global_game_time += 1
        self.lblGameTime.setText(
            f"Game Time:\n{self.game_time.hour():02d}:{self.game_time.minute():02d}:{self.game_time.second():02d}"
        )

    def time(self):
        self.saved_time += 1
        self.curr_time = self.curr_time.addSecs(1)

        self.game_timer
        self.update_time_label()

    def update_time_label(self):
        try:
            record_time = float(
                JSON_CONTENTS["records"][0][f"{self.grid_size_y}x{self.grid_size_x}"][
                    0
                ]["Time"]
            )
            record_moves = int(
                JSON_CONTENTS["records"][0][f"{self.grid_size_y}x{self.grid_size_x}"][
                    0
                ]["Moves"]
            )
            # str(datetime.timedelta(milliseconds=sum(self.average_time)))
            self.timerLabel.setText(
                f"Grid: {self.grid_size_y}x{self.grid_size_x}\nCurrent time: {self.curr_time.hour():02d}:{self.curr_time.minute():02d}:{self.curr_time.second():02d}    Moves: {self.current_moves}\nRecord Time: {str(datetime.timedelta(milliseconds=record_time))[:-3]}    Record Moves: {record_moves}"
            )
        except KeyError:
            JSON_CONTENTS["records"][0].update(
                {
                    str(self.grid_size_y)
                    + "x"
                    + str(self.grid_size_x): [
                        {"Moves": "Undfined", "Time": "Undefined"}
                    ]
                }
            )
            with open(JSON_FILE, "w") as f:
                json.dump(JSON_CONTENTS, f, indent=4)
        except ValueError:
            self.timerLabel.setText(
                f"Grid: {self.grid_size_y}x{self.grid_size_x}\nCurrent time: {self.curr_time.hour():02d}:{self.curr_time.minute():02d}:{self.curr_time.second():02d}    Moves: {self.current_moves}"
            )

    def generate_board(self):
        self.pressed_first_button = False

        self.clearLayout(self.gridLayout)
        screen = app.primaryScreen()
        height = screen.availableGeometry().height()
        width = screen.availableGeometry().width()
        max_height = height // self.grid_size_y // 2
        max_width = width // self.grid_size_x // 2
        self.button_size = min(max_height, max_width)
        self.font_size = self.button_size // 2
        self.move_history = []
        self.grid_run_time = [
            [None for y in range(self.grid_size_y)] for x in range(self.grid_size_x)
        ]
        self.button_array_list = [
            [None for y in range(self.grid_size_y)] for x in range(self.grid_size_x)
        ]
        count = 0
        for y in range(self.grid_size_y):
            for x in range(self.grid_size_x):
                button = QPushButton(self)
                # button.setIcon(QtGui.QIcon('myImage.jpg'))
                button.setFixedSize(self.button_size, self.button_size)
                button.setFlat(True)
                button.setCheckable(True)
                button.clicked.connect(partial(self.button_clicked, x, y))
                button.setChecked(True)
                # button.setMinimumSize(100,100)
                # button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                # button.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                if self.use_images:
                    # w.setPixmap(QtGui.QPixmap.fromImage(MIDDLE_LEFT))
                    button.setIconSize(QtCore.QSize(self.font_size, self.font_size))
                    if x == 0 and y == 0:
                        button.setIcon(QIcon(QPixmap(sprites.TOP_LEFT)))
                    elif x == self.grid_size_x - 1 and y == 0:
                        button.setIcon(QIcon(QPixmap(sprites.BOTTOM_LEFT)))
                    elif x == 0 and y == self.grid_size_y - 1:
                        button.setIcon(QIcon(QPixmap(sprites.TOP_RIGHT)))
                    elif x == self.grid_size_x - 1 and y == self.grid_size_y - 1:
                        button.setIcon(QIcon(QPixmap(sprites.BOTTOM_RIGHT)))
                    elif x == 0:
                        button.setIcon(QIcon(QPixmap(sprites.TOP)))
                    elif y == 0:
                        button.setIcon(QIcon(QPixmap(sprites.MIDDLE_LEFT)))
                    elif y == self.grid_size_y - 1:
                        button.setIcon(QIcon(QPixmap(sprites.MIDDLE_RIGHT)))
                    elif x == self.grid_size_x - 1:
                        button.setIcon(QIcon(QPixmap(sprites.BOTTOM)))
                    else:
                        button.setIcon(QIcon(QPixmap(sprites.MIDDLE)))
                else:
                    if x == 0 and y == 0:
                        button.setText("╔")
                    elif x == self.grid_size_x - 1 and y == 0:
                        button.setText("╚")
                    elif x == 0 and y == self.grid_size_y - 1:
                        button.setText("╗")
                    elif x == self.grid_size_x - 1 and y == self.grid_size_y - 1:
                        button.setText("╝")
                    elif x == 0:
                        button.setText("╦")
                    elif y == 0:
                        button.setText("╠")
                    elif y == self.grid_size_y - 1:
                        button.setText("╣")
                    elif x == self.grid_size_x - 1:
                        button.setText("╩")
                    else:
                        button.setText("╬")
                button.setFont(QFont("Times", self.font_size))
                self.gridLayout.addWidget(button, x, y)
                count += 1
                self.grid_run_time[x][y] = True
                self.button_array_list[x][y] = button

        # Simulate random key presses
        perc_to_press = random.uniform(0.35, 0.65)
        for x in range(self.grid_size_x):
            for y in range(self.grid_size_y):
                is_checked = random.random() < perc_to_press
                if is_checked:
                    self.button_clicked(x, y, automated_press=True)
        perc_to_press = random.uniform(0.35, 0.65)
        for y in range(self.grid_size_y):
            for x in range(self.grid_size_x):
                is_checked = random.random() < perc_to_press
                if is_checked:
                    self.button_clicked(x, y, automated_press=True)

        self.curr_time = QtCore.QTime(00, 00, 00)
        self.current_moves = 0
        self.saved_time = 0
        self.timer.stop()
        if self.currently_played == 0:
            self.overall_start_time = datetime.datetime.now()
            self.game_timer.start(1000)
        self.update_time_label()

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())

    @pyqtSlot()
    def revert_move(self):
        try:
            last_x = self.move_history[-1][0]
            last_y = self.move_history[-1][1]
            self.button_clicked(last_x, last_y, False)
            del self.move_history[-1]
        except IndexError:
            self.check_win()

    @pyqtSlot()
    def button_clicked(self, x, y, save_move=True, automated_press=False):
        if not automated_press:
            self.current_moves += 1
        self.update_time_label()
        if save_move:
            self.move_history.append([x, y])
        # center
        if self.grid_run_time[x][y] == True:
            self.grid_run_time[x][y] = False
            self.button_array_list[x][y].setChecked(False)
        else:
            self.grid_run_time[x][y] = True
            self.button_array_list[x][y].setChecked(True)
        # up
        if not y + 1 >= self.grid_size_y:
            if self.grid_run_time[x][y + 1] == True:
                self.grid_run_time[x][y + 1] = False
                self.button_array_list[x][y + 1].setChecked(False)
            else:
                self.grid_run_time[x][y + 1] = True
                self.button_array_list[x][y + 1].setChecked(True)
        # down
        if not y < 1:
            if self.grid_run_time[x][y - 1] == True:
                self.grid_run_time[x][y - 1] = False
                self.button_array_list[x][y - 1].setChecked(False)
            else:
                self.grid_run_time[x][y - 1] = True
                self.button_array_list[x][y - 1].setChecked(True)

        # left
        if not x < 1:
            if self.grid_run_time[x - 1][y] == True:
                self.grid_run_time[x - 1][y] = False
                self.button_array_list[x - 1][y].setChecked(False)
            else:
                self.grid_run_time[x - 1][y] = True
                self.button_array_list[x - 1][y].setChecked(True)

        # right
        if not x + 1 >= self.grid_size_x:
            if self.grid_run_time[x + 1][y] == True:
                self.grid_run_time[x + 1][y] = False
                self.button_array_list[x + 1][y].setChecked(False)
            else:
                self.grid_run_time[x + 1][y] = True
                self.button_array_list[x + 1][y].setChecked(True)

        self.check_win()

        if (
            not automated_press
            and not self.pressed_first_button
            and self.current_moves == 1
        ):
            self.start_time = datetime.datetime.now()
            self.curr_time = QtCore.QTime(00, 00, 00)
            self.timer.start(1000)
            self.time()
            self.pressed_first_button = True

    def keyPressEvent(self, event):
        # if event.key() == QtCore.Qt.Key_N:
        #     self.generate_board()
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)

    def check_win(self):
        count = 0
        for row in self.grid_run_time:
            for col in row:
                if col == True:
                    count += 1
        if count == self.grid_size_x * self.grid_size_y:
            self.currently_played += 1
            self.setWindowTitle(f"Flip {self.currently_played}/{self.game_limit}")
            self.end_time = datetime.datetime.now()
            self.overall_end_time = datetime.datetime.now()
            self.average_score.append(self.current_moves)
            game_time_diff = self.overall_end_time - self.overall_start_time
            diff = self.end_time - self.start_time
            elapsed_time = int((diff.seconds * 1000) + (diff.microseconds / 1000))
            game_elapsed_time = int(
                (game_time_diff.seconds * 1000) + (game_time_diff.microseconds / 1000)
            )
            self.average_time.append(elapsed_time)
            self.saved_time = elapsed_time

            self.save_scores()
            self.curr_time = QtCore.QTime(00, 00, 00)
            self.current_moves = 0
            self.saved_time = 0
            self.timer.stop()
            self.update_time_label()
            if self.currently_played == self.game_limit:
                self.game_timer.stop()
                average_time = str(
                    datetime.timedelta(
                        milliseconds=sum(self.average_time)
                        / float(len(self.average_time))
                    )
                )[:-3]

                total_time = str(
                    datetime.timedelta(milliseconds=sum(self.average_time))
                )[:-3]
                total_game_time = str(
                    datetime.timedelta(milliseconds=game_elapsed_time)
                )[:-3]
                longest_time_index = 0
                quickest_time_index = 0
                temp_longest_time_value = 0
                temp_quickest_time_value = 999999999999999
                for i, time_m in enumerate(self.average_time):
                    if temp_longest_time_value < time_m:
                        longest_time_index = i
                        temp_longest_time_value = time_m
                    if temp_quickest_time_value > time_m:
                        quickest_time_index = i
                        temp_quickest_time_value = time_m
                quickest_time = str(
                    datetime.timedelta(
                        milliseconds=self.average_time[quickest_time_index]
                    )
                )[:-3]
                longest_time = str(
                    datetime.timedelta(
                        milliseconds=self.average_time[longest_time_index]
                    )
                )[:-3]
                reply = QMessageBox.information(
                    self,
                    f"Your score for {self.game_limit} games.",
                    f"""Your scores for {self.game_limit} games is:
                    
Average Moves: {int(sum(self.average_score) / float(len(self.average_score)))}
Average Time: {average_time}

Quickest Time: {quickest_time}
With {self.average_score[quickest_time_index]} Moves.

Slowest Time: {longest_time}
With {self.average_score[longest_time_index]} Moves.

Total time for solving {self.game_limit} puzzles: {total_time}

Overall game time: {total_game_time}
Total Moves: {int(sum(self.average_score))}

Clicks Per Second: {round(sum(self.average_score)/(sum(self.average_time)/1000), 2)}
""",
                    QMessageBox.Ok,
                    QMessageBox.Ok,
                )
                self.average_score.clear()
                self.average_time.clear()
                self.currently_played = 0
                self.global_game_time = 0
                self.game_time = QtCore.QTime(00, 00, 00)
                self.lblGameTime.setText(
                    f"Game Time:\n{self.game_time.hour():02d}:{self.game_time.minute():02d}:{self.game_time.second():02d}"
                )

                self.setWindowTitle(f"Flip {self.currently_played}/{self.game_limit}")
            if self.show_play_again_dialog == False:
                reply = QMessageBox.question(
                    self,
                    "Play again?",
                    "Do you want to play again?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes,
                )
                if reply == QMessageBox.Yes:
                    self.generate_board()
                else:
                    self.close()
            else:
                self.generate_board()

    def save_scores(self):
        try:
            record_time = float(
                JSON_CONTENTS["records"][0][f"{self.grid_size_y}x{self.grid_size_x}"][
                    0
                ]["Time"]
            )
            record_moves = int(
                JSON_CONTENTS["records"][0][f"{self.grid_size_y}x{self.grid_size_x}"][
                    0
                ]["Moves"]
            )
        except ValueError:
            record_time = self.saved_time
            record_moves = self.current_moves
        if self.saved_time <= record_time and self.current_moves <= record_moves:
            JSON_CONTENTS["records"][0][f"{self.grid_size_y}x{self.grid_size_x}"][0][
                "Time"
            ] = self.saved_time
            JSON_CONTENTS["records"][0][f"{self.grid_size_y}x{self.grid_size_x}"][0][
                "Moves"
            ] = self.current_moves
            with open(JSON_FILE, "w") as f:
                json.dump(JSON_CONTENTS, f, indent=4)


if __name__ == "__main__":

    with open(JSON_FILE) as file:
        JSON_CONTENTS = json.load(file)

    app = QApplication(sys.argv)
    window = Ui()
    app.exec_()
