import sys
from PyQt5.QtWidgets import QApplication
from login_window import LoginWindow

def main():
    app = QApplication(sys.argv)
    
    app.setStyleSheet("""
        QWidget {
            background-color: #F8FFF8;
            color: #1A4D2E;
            font-family: "Microsoft YaHei";
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 8px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QLineEdit {
            border: 2px solid #81C784;
            border-radius: 5px;
            padding: 5px;
            background-color: white;
        }
    """)

    login_win = LoginWindow()
    login_win.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
