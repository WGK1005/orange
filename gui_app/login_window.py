from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QLineEdit, QPushButton, QMessageBox, QCheckBox, QScrollArea
)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt
from pathlib import Path
from interfaces import DatabaseAPI


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("智能农业小车 - 用户登录")
        self.resize(900, 500)
        self.db_api = DatabaseAPI()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        
        # ==================== 左侧：玉米图片 ====================
        left_panel = QLabel()
        left_panel.setStyleSheet("background-color: #F0F4E8;")
        left_panel.setAlignment(Qt.AlignCenter)
        left_panel.setMinimumSize(300, 400)
        
        # 加载玉米图片
        corn_img_path = Path(__file__).parent / "assest" / "corn.jpg"
        if corn_img_path.exists():
            pixmap = QPixmap(str(corn_img_path))
            left_panel.setPixmap(pixmap)
            left_panel.setScaledContents(True)  # 图片自动填充整个左侧区域
        else:
            left_panel.setText("玉米图片\n加载失败")
            left_panel.setStyleSheet("background-color: #F0F4E8; color: #999; font-size: 14px;")
        
        # ==================== 右侧：登录表单 ====================
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        right_layout.setContentsMargins(30, 40, 30, 40)
        
        # 标题
        title = QLabel("🌽 苗健谷满仓智能终端")
        title_font = QFont("Microsoft YaHei", 18, QFont.Bold)
        title.setFont(title_font)
        title.setStyleSheet("color: #2E7D32;")
        right_layout.addWidget(title)
        
        # 副标题
        subtitle = QLabel("用户登录")
        subtitle_font = QFont("Microsoft YaHei", 12)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: #558B2F;")
        right_layout.addWidget(subtitle)
        
        # 分隔线
        separator = QLabel("─" * 30)
        separator.setStyleSheet("color: #81C784;")
        right_layout.addWidget(separator)
        
        # 用户名
        user_label = QLabel("用户名")
        user_label.setStyleSheet("color: #2E7D32; font-weight: bold;")
        right_layout.addWidget(user_label)
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("请输入用户名")
        self.user_input.setMinimumHeight(40)
        right_layout.addWidget(self.user_input)
        
        # 密码
        pwd_label = QLabel("密码")
        pwd_label.setStyleSheet("color: #2E7D32; font-weight: bold;")
        right_layout.addWidget(pwd_label)
        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("请输入密码")
        self.pwd_input.setEchoMode(QLineEdit.Password)
        self.pwd_input.setMinimumHeight(40)
        right_layout.addWidget(self.pwd_input)
        
        # 忘记密码链接
        forgot_layout = QHBoxLayout()
        forgot_layout.addStretch()
        self.btn_forgot = QPushButton("忘记密码？")
        self.btn_forgot.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #1976D2;
                border: none;
                text-decoration: underline;
                padding: 0px;
            }
            QPushButton:hover {
                color: #0D47A1;
            }
        """)
        self.btn_forgot.setMaximumWidth(100)
        forgot_layout.addWidget(self.btn_forgot)
        right_layout.addLayout(forgot_layout)
        
        # 隐私保护协议勾选框
        self.agree_checkbox = QCheckBox("我同意《隐私保护协议》和《用户服务条款》")
        self.agree_checkbox.setStyleSheet("color: #2E7D32;")
        right_layout.addWidget(self.agree_checkbox)
        
        # 按钮区
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        
        self.btn_login = QPushButton("登录")
        self.btn_login.setMinimumHeight(45)
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.btn_register = QPushButton("注册新账户")
        self.btn_register.setMinimumHeight(45)
        self.btn_register.setStyleSheet("""
            QPushButton {
                background-color: #81C784;
                color: white;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #66BB6A;
            }
        """)
        
        btn_layout.addWidget(self.btn_login)
        btn_layout.addWidget(self.btn_register)
        right_layout.addLayout(btn_layout)
        
        right_layout.addStretch()
        
        # 组合左右两侧
        main_layout.addWidget(left_panel, 1)
        right_panel = QWidget()
        right_panel.setLayout(right_layout)
        main_layout.addWidget(right_panel, 1)
        
        self.setLayout(main_layout)
        
        # 绑定事件
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_register.clicked.connect(self.handle_register)
        self.btn_forgot.clicked.connect(self.handle_forgot)

    def handle_login(self):
        user = self.user_input.text().strip()
        pwd = self.pwd_input.text().strip()
        
        if not user or not pwd:
            QMessageBox.warning(self, "提示", "请输入用户名和密码")
            return
        
        if not self.agree_checkbox.isChecked():
            QMessageBox.warning(self, "提示", "请同意隐私保护协议")
            return
        
        if self.db_api.check_login(user, pwd):
            from main_window import MainWindow
            self.main_app = MainWindow(user_name=user)
            self.main_app.show()
            self.close()
        else:
            QMessageBox.warning(self, "失败", "登录失败或数据库接口未连接")

    def handle_register(self):
        user = self.user_input.text().strip()
        pwd = self.pwd_input.text().strip()
        
        if not user or not pwd:
            QMessageBox.warning(self, "提示", "请输入用户名和密码")
            return
        
        if not self.agree_checkbox.isChecked():
            QMessageBox.warning(self, "提示", "请同意隐私保护协议")
            return
        
        if self.db_api.register_user(user, pwd):
            QMessageBox.information(self, "成功", "注册成功！(实际数据库预留)")
        else:
            QMessageBox.warning(self, "失败", "注册失败或用户已存在")

    def handle_forgot(self):
        QMessageBox.information(self, "找回密码", 
                              "请联系管理员：adminWGC@163.com\n\n"
                              "或通过系统菜单中的\"隐私\"选项进行账户恢复")
