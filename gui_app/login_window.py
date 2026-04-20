from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox
)
from interfaces import DatabaseAPI

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能农业小车 - 用户登录 (农业主题版)")
        self.resize(400, 300)
        self.db_api = DatabaseAPI()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel("🌽 玉米叶片智能除草施肥终端")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2E7D32; alignment: center;")
        layout.addWidget(title)

        # 输入框
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("请输入用户名")
        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("请输入密码")
        self.pwd_input.setEchoMode(QLineEdit.Password)
        
        layout.addWidget(self.user_input)
        layout.addWidget(self.pwd_input)

        # 按钮区
        btn_layout = QHBoxLayout()
        self.btn_login = QPushButton("登录")
        self.btn_register = QPushButton("注册")
        
        btn_layout.addWidget(self.btn_login)
        btn_layout.addWidget(self.btn_register)
        layout.addLayout(btn_layout)

        # 绑定事件
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_register.clicked.connect(self.handle_register)

        self.setLayout(layout)

    def handle_login(self):
        user = self.user_input.text()
        pwd = self.pwd_input.text()
        if self.db_api.check_login(user, pwd):
            from main_window import MainWindow
            self.main_app = MainWindow()
            self.main_app.show()
            self.close()
        else:
            QMessageBox.warning(self, "失败", "登录失败或数据库接口未连接")

    def handle_register(self):
        user = self.user_input.text()
        pwd = self.pwd_input.text()
        if self.db_api.register_user(user, pwd):
            QMessageBox.information(self, "成功", "注册成功！(实际数据库预留)")
