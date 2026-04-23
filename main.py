import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt6.QtCore import Qt

from config.settings import APP_NAME, APP_VERSION
from database.db import init_db, close_db


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} {APP_VERSION}")
        self.setMinimumSize(900, 600)

        placeholder = QLabel("Interface à venir — base de données initialisée.")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(placeholder)


def main():
    init_db()
    print("Base de données initialisée.")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    exit_code = app.exec()
    close_db()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
