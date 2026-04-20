from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QLineEdit, QPushButton, QLabel, 
    QProgressBar, QSplitter, QMenuBar, QAction, QStackedWidget
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont
from interfaces import (
    AI_API, BluetoothAPI, STM32API, CameraAPI
)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌽 农业履带小车终端系统 - 玉米剪切及施肥")
        # 设置初始基准比例
        self.base_width = 1000
        self.base_height = 700
        self.resize(self.base_width, self.base_height)
        
        # 接口实例化
        self.ai_api = AI_API()
        self.bt_api = BluetoothAPI()
        self.stm32_api = STM32API()
        self.cam_api = CameraAPI()
        
        # 初始化 UI
        self.init_menu()
        self.init_ui()

    def init_menu(self):
        """初始化左上角的菜单栏 (设置、隐私、操作等)"""
        menubar = self.menuBar()
        menubar.setStyleSheet("background-color: #E8F5E9; color: #1A4D2E;")
        
        # 设置菜单
        settings_menu = menubar.addMenu("⚙️ 设置")
        settings_menu.addAction("系统参数...")
        settings_menu.addAction("AI 模型接口设置")
        
        # 隐私菜单
        privacy_menu = menubar.addMenu("🛡️ 隐私")
        privacy_menu.addAction("清除本地日志")
        privacy_menu.addAction("数据加密配置")
        
        # 操作菜单
        ops_menu = menubar.addMenu("🔧 操作")
        ops_menu.addAction("强制重置下位机")
        ops_menu.addAction("停止所有电机动作")
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 整体主布局：纵向 (顶部导航栏 + 下方内容区)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(10, 5, 10, 10)
        
        # -------------------- 顶部独立导航栏 --------------------
        nav_layout = QHBoxLayout()
        self.btn_nav_control = QPushButton("🏠 智能小车主控界面")
        self.btn_nav_map = QPushButton("🗺️ 卫星地图与路线 (高德地图预留)")
        
        # 样式美化
        nav_style = """
            QPushButton {
                background-color: transparent; 
                color: #2E7D32; 
                font-size: 16px; 
                border: 2px solid #81C784;
                border-radius: 5px;
            }
            QPushButton:hover { background-color: #C8E6C9; }
        """
        self.btn_nav_control.setStyleSheet(nav_style)
        self.btn_nav_map.setStyleSheet(nav_style)
        
        nav_layout.addWidget(self.btn_nav_control)
        nav_layout.addWidget(self.btn_nav_map)
        nav_layout.addStretch()
        
        root_layout.addLayout(nav_layout)

        # -------------------- 视图堆叠区 --------------------
        self.stacked_widget = QStackedWidget()
        root_layout.addWidget(self.stacked_widget)
        
        # 将原主界面组件放进第一页: Controller View
        self.init_control_view()
        # 将高德地图接口放进第二页: Map View
        self.init_map_view()
        
        # 绑定导航栏点击事件
        self.btn_nav_control.clicked.connect(lambda: self.switch_view(0))
        self.btn_nav_map.clicked.connect(lambda: self.switch_view(1))

    def switch_view(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
    def init_map_view(self):
        """独立的高德地图模块（预留）"""
        map_widget = QWidget()
        map_layout = QVBoxLayout(map_widget)
        
        title = QLabel("🛰️ 高德地图位置服务 (开发预留)")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1976D2;")
        
        # 地图显示预留区
        map_view_placeholder = QLabel("正在接入高德地图定位API...\n此页面独立于主控界面，实现通过左上角的按键进行多模块无缝切换。")
        map_view_placeholder.setAlignment(Qt.AlignCenter)
        map_view_placeholder.setStyleSheet("""
            background-color: #E3F2FD; 
            border: 3px solid #64B5F6; 
            border-radius: 10px; 
            font-size: 18px;
            color: #1565C0;
        """)
        
        map_layout.addWidget(title)
        map_layout.addWidget(map_view_placeholder)
        self.stacked_widget.addWidget(map_widget)

    def init_control_view(self):
        """原有的小车与AI控制模块"""
        control_widget = QWidget()
        main_layout = QHBoxLayout(control_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        splitter = QSplitter(Qt.Horizontal)

        # ====== 原左侧：主视界与状态 ======
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        self.cam_label = QLabel("📷 香橙派画面串流 ")
        self.cam_label.setStyleSheet("background-color: #E8F5E9; border: 2px dashed #4CAF50; font-size: 24px;")
        self.cam_label.setAlignment(Qt.AlignCenter)
        self.cam_label.setMinimumSize(500, 400)
        left_layout.addWidget(self.cam_label)

        status_layout = QVBoxLayout()
        status_title = QLabel("⚙️ 设备与传感状态 (STM32 & 蓝牙通信)")
        status_title.setStyleSheet("font-weight: bold; color: #2E7D32;")
        status_layout.addWidget(status_title)

        batt_layout = QHBoxLayout()
        batt_label = QLabel("🔋 电池可用电量:")
        self.batt_bar = QProgressBar()
        self.batt_bar.setValue(self.stm32_api.get_battery_level())
        batt_layout.addWidget(batt_label)
        batt_layout.addWidget(self.batt_bar)
        
        zinc_layout = QHBoxLayout()
        zinc_label = QLabel("🧴 锌肥余量状况:")
        self.zinc_bar = QProgressBar()
        self.zinc_bar.setValue(self.stm32_api.get_zinc_level())
        self.zinc_bar.setStyleSheet("QProgressBar::chunk {background-color: #FFC107;}")
        zinc_layout.addWidget(zinc_label)
        zinc_layout.addWidget(self.zinc_bar)

        self.log_box = QTextEdit()
        self.log_box.setReadOnly(True)
        self.log_box.setStyleSheet("background-color: #333; color: #00FF00; font-family: monospace;")
        self.log_box.append(">>> 系统初始化完毕。等待蓝牙应用接入...")
        self.log_box.append(">>> STM32 407VGT6 连接正常。")
        self.log_box.setFixedHeight(120)

        status_layout.addLayout(batt_layout)
        status_layout.addLayout(zinc_layout)
        status_layout.addWidget(self.log_box)
        left_layout.addLayout(status_layout)
        
        # ====== 原右侧：AI 大模型聊天 ======
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # 增加 DeepSeek 图标并在标题使用 HTML 布局嵌入
        icon_path = "D:/YOLO/corn/code/gui_app/assest/deepseek.webp"
        ai_title = QLabel(f"<img src='{icon_path}' width='28' height='28' align='middle'> 农智 AI 助手 (玉米与施肥大模型)")
        ai_title.setStyleSheet("font-weight: bold; color: #1976D2; font-size: 16px;")
        right_layout.addWidget(ai_title)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("background-color: #FFFFFF;")
        self.chat_display.append("[AI助手] 您好，专家系统已就绪，可随时分析玉米叶片剪切策略或锌肥配置方案。")

        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("请输入您的问题...")
        self.send_btn = QPushButton("发送(Enter)")

        self.send_btn.clicked.connect(self.send_to_ai)
        self.chat_input.returnPressed.connect(self.send_to_ai)

        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(self.send_btn)

        right_layout.addWidget(self.chat_display)
        right_layout.addLayout(input_layout)

        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        # 固定左与右的基础拉伸比例，在放大窗口时，会按此倍率均匀拉伸
        splitter.setStretchFactor(0, 6) 
        splitter.setStretchFactor(1, 4) 

        main_layout.addWidget(splitter)
        self.stacked_widget.addWidget(control_widget)

    def resizeEvent(self, event):
        """窗口重设大小时，做一次比例自适应计算，防止内部(特别是摄像头模块)畸变更小"""
        super().resizeEvent(event)
        
        # 通过拦截缩放事件，动态维护核心区域（如香橙派推流画面）の 4:3 比例
        # 防止用户长高不一致地随意拉长窗口导致的重叠畸变
        try:
            cam_w = self.cam_label.width()
            target_h = int(cam_w * 0.75) # 4:3 比例
            # 锁定画面高度，其他多余空间交给日志区/空白自适应
            self.cam_label.setFixedHeight(target_h)
        except AttributeError:
            pass

    def send_to_ai(self):
        user_msg = self.chat_input.text()
        if not user_msg: return

        self.chat_display.append(f"<b style='color:green;'>[控制端]:</b> {user_msg}")
        self.chat_input.clear()
        
        reply = self.ai_api.chat_with_model(user_msg)
        self.chat_display.append(f"<b style='color:blue;'>[AI助手]:</b> {reply}")

