from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QLineEdit, QPushButton, QLabel, QComboBox, QFileDialog, QMessageBox, QInputDialog,
    QProgressBar, QSplitter, QMenuBar, QAction, QStackedWidget, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QTextOption, QPixmap, QTextCursor
import subprocess
import shutil
from pathlib import Path
import sys
import os
from html import escape as html_escape

# 添加上级目录到Python路径，以便导入path_manager
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from path_manager import path_manager

from interfaces import (
    AI_API, BluetoothAPI, STM32API, CameraAPI, DatabaseAPI
)

class MainWindow(QMainWindow):
    def __init__(self, user_name="我"):
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
        self.upload_dir = path_manager.assest_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.last_uploaded_image = None
        self.cam_default_text = "📷 香橙派画面串流 "
        self.image_query_mode = False
        self.current_result_image_path = None
        self.user_name = user_name or "我"
        self.user_avatar_path = None
        
        # 初始化 UI
        self.init_menu()
        self.init_ui()

    def init_menu(self):
        """初始化左上角的菜单栏 (设置、隐私、操作等)"""
        menubar = self.menuBar()
        menubar.setStyleSheet("background-color: #E8F5E9; color: #1A4D2E;")
        
        # 设置菜单
        settings_menu = menubar.addMenu("设置")
        act_sys = settings_menu.addAction("系统参数...")
        act_ai = settings_menu.addAction("AI 模型接口设置")
        act_provider = settings_menu.addAction("API 服务提供商")
        act_apikey = settings_menu.addAction("API key")
        act_tokens = settings_menu.addAction("回复最大 Token 数")        
        act_model = settings_menu.addAction("模型选择")
        act_aux = settings_menu.addAction("辅助模型")
        act_avatar = settings_menu.addAction("用户头像设置")

        act_sys.triggered.connect(self.open_system_settings)
        act_ai.triggered.connect(self.open_ai_settings)
        act_provider.triggered.connect(self.set_api_provider)
        act_apikey.triggered.connect(self.set_api_key)
        act_tokens.triggered.connect(self.set_max_tokens)
        act_model.triggered.connect(self.select_model)
        act_aux.triggered.connect(self.select_aux_model)
        act_avatar.triggered.connect(self.set_user_avatar)

        # 隐私菜单
        privacy_menu = menubar.addMenu("隐私")
        act_clear = privacy_menu.addAction("清除本地日志")
        act_encrypt = privacy_menu.addAction("数据加密配置")
        act_account = privacy_menu.addAction("账户")

        act_clear.triggered.connect(self.clear_local_logs)
        act_encrypt.triggered.connect(self.configure_encryption)
        act_account.triggered.connect(self.manage_account)

        # 操作菜单
        ops_menu = menubar.addMenu("操作")
        act_reset = ops_menu.addAction("强制重置下位机")
        act_stop = ops_menu.addAction("停止所有电机动作")

        act_reset.triggered.connect(self.force_reset_lower)
        act_stop.triggered.connect(self.stop_all_motors)

        # 设备菜单
        dev_menu = menubar.addMenu("设备")
        act_serial = dev_menu.addAction("设备序列号")
        act_perf = dev_menu.addAction("性能")

        act_serial.triggered.connect(self.show_device_serial)
        act_perf.triggered.connect(self.show_performance)
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 整体主布局：纵向 (顶部导航栏 + 下方内容区)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(10, 5, 10, 10)
        
        # -------------------- 顶部独立导航栏 --------------------
        nav_layout = QHBoxLayout()
        self.btn_nav_control = QPushButton("智能小车主控界面")
        self.btn_nav_map = QPushButton("卫星地图与路线 (高德地图预留)")
        
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
        
        nav_layout.addStretch(2)
        nav_layout.addWidget(self.btn_nav_control)
        nav_layout.addWidget(self.btn_nav_map)
        nav_layout.addStretch(1)
        
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
        
        self.cam_label = QLabel(self.cam_default_text)
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
        # 使用相对路径查找资产目录下的图标（相对于本文件）
        icon_path = Path(__file__).resolve().parent / 'assest' / 'deepseek.webp'
        ai_title = QLabel(f"<img src='{icon_path.as_posix()}' width='28' height='28' align='middle'> 农智 AI 助手 (玉米与施肥大模型)")
        ai_title.setStyleSheet("font-weight: bold; color: #1976D2; font-size: 16px;")
        right_layout.addWidget(ai_title)

        model_panel = QWidget()
        model_panel_layout = QVBoxLayout(model_panel)
        model_panel_layout.setContentsMargins(0, 0, 0, 0)
        model_panel_layout.setSpacing(6)

        main_model_row = QHBoxLayout()
        self.main_model_label = QLabel(f"主模型：{self.ai_api.main_model}")
        self.main_model_label.setStyleSheet("color: #1A4D2E; font-weight: bold;")
        main_model_hint = QLabel("用于常规农业问答与设备推理")
        main_model_hint.setStyleSheet("color: #5F6F5F; font-size: 12px;")
        main_model_row.addWidget(self.main_model_label)
        main_model_row.addStretch()
        main_model_row.addWidget(main_model_hint)

        weather_model_row = QHBoxLayout()
        weather_model_label = QLabel("辅助模型：")
        weather_model_label.setStyleSheet("color: #1A4D2E; font-weight: bold;")
        self.weather_model_combo = QComboBox()
        self.weather_model_combo.addItems([
            "GPT-4o-mini（推荐，低成本）",
            "DeepSeek 低成本轻量模型",
            "Qwen-Turbo / 其他低成本AI"
        ])
        self.weather_model_combo.setCurrentIndex(0)
        weather_model_hint = QLabel("专门回答天气相关问题")
        weather_model_hint.setStyleSheet("color: #5F6F5F; font-size: 12px;")
        weather_model_row.addWidget(weather_model_label)
        weather_model_row.addWidget(self.weather_model_combo)
        weather_model_row.addWidget(weather_model_hint)

        model_panel_layout.addLayout(main_model_row)
        model_panel_layout.addLayout(weather_model_row)
        right_layout.addWidget(model_panel)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.chat_display.setMinimumHeight(0)
        self.chat_display.setLineWrapMode(QTextEdit.WidgetWidth)
        self.chat_display.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.chat_display.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_display.setStyleSheet("background-color: #F7F9FB; font-size: 15px;")
        self.append_chat_message(
            "assistant",
            "您好，专家系统已就绪，可随时分析玉米叶片剪切策略或锌肥配置方案。"
        )

        input_layout = QHBoxLayout()
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("请输入您的问题...")
        self.send_btn = QPushButton("发送(Enter)")
        self.upload_btn = QPushButton("上传图片并分析")
        self.exit_image_mode_btn = QPushButton("退出图片询问模式")
        self.exit_image_mode_btn.setEnabled(False)

        self.send_btn.clicked.connect(self.send_to_ai)
        self.chat_input.returnPressed.connect(self.send_to_ai)
        self.upload_btn.clicked.connect(self.upload_and_analyze_image)
        self.exit_image_mode_btn.clicked.connect(self.exit_image_query_mode)

        input_layout.addWidget(self.chat_input)
        input_layout.addWidget(self.upload_btn)
        input_layout.addWidget(self.exit_image_mode_btn)
        input_layout.addWidget(self.send_btn)

        right_layout.addWidget(self.chat_display, 1)
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
            if self.image_query_mode and self.current_result_image_path:
                self.update_cam_image(self.current_result_image_path)
        except AttributeError:
            pass

    def send_to_ai(self):
        user_msg = self.chat_input.text()
        if not user_msg: return

        self.append_chat_message("user", user_msg)
        self.chat_input.clear()
        
        reply, model_tag = self.ai_api.chat_auto(user_msg)
        self.append_chat_message("assistant", f"{reply}\n\n{model_tag}")

    def upload_and_analyze_image(self):
        image_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择要上传的图片",
            "",
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.webp)"
        )
        if not image_path:
            return

        source_path = Path(image_path)
        target_path = self.upload_dir / source_path.name

        try:
            shutil.copy2(str(source_path), str(target_path))
            self.last_uploaded_image = target_path
            self.append_chat_message("system", f"图片已暂存到 {target_path}")
        except Exception as exc:
            QMessageBox.critical(self, "上传失败", f"图片暂存失败：{exc}")
            return

        # 使用仓库根目录下的 Test3.py（相对路径），方便移植
        script_path = Path(__file__).resolve().parents[1] / "Test3.py"
        try:
            process = subprocess.run(
                [sys.executable, str(script_path), str(target_path)],
                cwd=str(script_path.parent),
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=180,
            )
        except Exception as exc:
            QMessageBox.critical(self, "运行失败", f"调用视觉脚本失败：{exc}")
            return

        if process.stdout:
            stdout_html = process.stdout.strip().replace("\n", "<br>")
            self.append_chat_message("system", f"视觉脚本输出：\n{process.stdout.strip()}")
        if process.returncode != 0:
            stderr_html = process.stderr.strip().replace("\n", "<br>")
            self.append_chat_message("system", f"视觉脚本错误：\n{process.stderr.strip()}")
            return

        result_image_path = target_path.with_name("result.jpg")
        summary_text = self.build_image_summary(result_image_path, process.stdout)
        helper_reply = self.ai_api.chat_with_weather_model(summary_text)
        main_prompt = (
            f"请根据下面由辅助模型整理的图片标注结果进行农业分析，给出简洁建议：\n"
            f"{helper_reply}"
        )
        main_reply = self.ai_api.chat_with_model(main_prompt)

        self.append_chat_message("assistant", f"辅助模型描述：\n{helper_reply}")
        self.append_chat_message("assistant", f"主模型分析：\n{main_reply}")

        self.enter_image_query_mode(result_image_path)

    def build_image_summary(self, result_image_path: Path, stdout_text: str) -> str:
        leaf_count = "未知"
        for line in stdout_text.splitlines():
            if line.startswith("✅ 完成：检测到"):
                leaf_count = line.split("检测到", 1)[-1].split("片叶子", 1)[0].strip()
                break

        return (
            f"已完成图片标注，检测结果图路径：{result_image_path}。"
            f"脚本识别到的叶片数量为：{leaf_count}。"
            "请用简洁中文描述这张图的标注结果、叶片数量和可能的农艺意义。"
        )

    def enter_image_query_mode(self, result_image_path: Path):
        self.image_query_mode = True
        self.current_result_image_path = Path(result_image_path)
        self.exit_image_mode_btn.setEnabled(True)
        self.update_cam_image(self.current_result_image_path)

    def exit_image_query_mode(self):
        self.image_query_mode = False
        self.current_result_image_path = None
        self.exit_image_mode_btn.setEnabled(False)
        self.cam_label.setPixmap(QPixmap())
        self.cam_label.setText(self.cam_default_text)

    def update_cam_image(self, image_path: Path):
        pixmap = QPixmap(str(image_path))
        if pixmap.isNull():
            self.cam_label.setPixmap(QPixmap())
            self.cam_label.setText("图片加载失败")
            return

        scaled_pixmap = pixmap.scaled(
            self.cam_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )
        self.cam_label.setText("")
        self.cam_label.setPixmap(scaled_pixmap)

    def _build_avatar_html(self, role: str) -> str:
        if role == "user":
            if self.user_avatar_path and Path(self.user_avatar_path).exists():
                avatar_src = Path(self.user_avatar_path).as_posix()
                return (
                    f"<img src='{avatar_src}' width='38' height='38' "
                    f"style='border-radius:19px; border:1px solid #9AD6A7;' />"
                )
            fallback = html_escape((self.user_name[:1] or "U").upper())
            return (
                f"<span style='display:inline-block; width:38px; height:38px; line-height:38px; "
                f"text-align:center; border-radius:14px; background:#DFF3E3; color:#2E7D32; "
                f"font-size:16px; font-weight:700; border:1px solid #9AD6A7;'>{fallback}</span>"
            )

        return (
            "<span style='display:inline-block; width:38px; height:38px; line-height:38px; "
            "text-align:center; border-radius:14px; background:#E3F2FD; color:#1976D2; "
            "font-size:16px; font-weight:700; border:1px solid #C9D6E2;'>AI</span>"
        )

    def append_chat_message(self, role: str, message: str):
        """以聊天气泡的方式追加消息。用户右侧、AI 左侧、系统居中。"""
        text = html_escape(message).replace("\n", "<br>")

        if role == "user":
            bubble_bg = "#DFF3E3"
            border = "#9AD6A7"
            label = self.user_name
            label_color = "#2E7D32"
            avatar_html = self._build_avatar_html("user")
        elif role == "assistant":
            bubble_bg = "#FFFFFF"
            border = "#C9D6E2"
            label = "智能体"
            label_color = "#1976D2"
            avatar_html = self._build_avatar_html("assistant")
        else:
            bubble_bg = "#EEF2F6"
            border = "#D5DCE3"
            label = "系统"
            label_color = "#607D8B"
            avatar_html = ""

        if role == "user":
            html = f"""
            <table width='100%' cellspacing='0' cellpadding='0' style='margin:8px 0;'>
                <tr>
                    <td align='right'>
                        <table cellspacing='0' cellpadding='0' style='max-width:80%;'>
                            <tr>
                                <td align='right' style='padding-bottom:6px;'>
                                    <span style='font-size:14px; color:{label_color}; font-weight:700; margin-right:10px;'>{html_escape(label)}</span>
                                    {avatar_html}
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <div style='background:{bubble_bg}; border:1px solid {border}; border-radius:18px; padding:14px 16px; font-size:16px; line-height:1.75; color:#1F2937; white-space:normal; text-align:left;'>{text}</div>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
            """
        elif role == "assistant":
            html = f"""
            <table width='100%' cellspacing='0' cellpadding='0' style='margin:8px 0;'>
                <tr>
                    <td align='left'>
                        <table cellspacing='0' cellpadding='0' style='max-width:80%;'>
                            <tr>
                                <td align='left' style='padding-bottom:6px;'>
                                    {avatar_html}
                                    <span style='font-size:14px; color:{label_color}; font-weight:700; margin-left:10px;'>{html_escape(label)}</span>
                                </td>
                            </tr>
                            <tr>
                                <td>
                                    <div style='background:{bubble_bg}; border:1px solid {border}; border-radius:18px; padding:14px 16px; font-size:16px; line-height:1.75; color:#1F2937; white-space:normal; text-align:left;'>{text}</div>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            </table>
            """
        else:
            html = f"""
            <div style='width:100%; margin:8px 0; text-align:center;'>
                <div style='display:inline-block; max-width:80%;'>
                    <div style='font-size:14px; color:{label_color}; font-weight:700; margin-bottom:6px; text-align:center;'>{html_escape(label)}</div>
                    <div style='background:{bubble_bg}; border:1px solid {border}; border-radius:18px; padding:14px 16px; font-size:16px; line-height:1.75; color:#1F2937; white-space:normal; text-align:left;'>{text}</div>
                </div>
            </div>
            """
        self.chat_display.append(html)
        self.chat_display.moveCursor(QTextCursor.End)

    # -------------------- 菜单操作实现 --------------------
    def open_system_settings(self):
        QMessageBox.information(self, "系统参数", "系统参数界面暂未实现，后续可在此处添加高级配置。")

    def open_ai_settings(self):
        # 展示当前 AI 接口配置并允许修改
        url, ok = QInputDialog.getText(self, "AI 模型接口设置", "API 地址：", text=self.ai_api.api_url)
        if ok and url:
            self.ai_api.api_url = url.strip()
            QMessageBox.information(self, "已保存", f"已更新 AI 接口地址：{self.ai_api.api_url}")

    def set_api_provider(self):
        provider, ok = QInputDialog.getText(self, "API 服务提供商", "请输入第三方提供商地址或备注：", text=self.ai_api.api_url)
        if ok and provider:
            self.ai_api.api_url = provider.strip()
            self.log_box.append(f"[设置] API 服务提供商已设置为：{self.ai_api.api_url}")

    def set_api_key(self):
        key, ok = QInputDialog.getText(self, "API Key", "请输入 API Key：", echo=QInputDialog.Normal)
        if ok:
            self.ai_api.api_key = key.strip()
            QMessageBox.information(self, "已保存", "API Key 已更新（已隐藏显示）。")

    def set_max_tokens(self):
        tokens, ok = QInputDialog.getInt(self, "回复最大 Token 数", "请输入最大 token 数：", value=1024, min=16, max=65536)
        if ok:
            # 目前为演示，保存到 ai_api 的一个属性
            setattr(self.ai_api, 'max_tokens', tokens)
            QMessageBox.information(self, "已保存", f"回复最大 Token 数已设置为 {tokens}")

    def select_model(self):
        models = ["gpt-4o-mini", "deepseek-v3", "qwen-turbo"]
        model, ok = QInputDialog.getItem(self, "选择主模型", "主模型：", models, current=0, editable=False)
        if ok and model:
            self.ai_api.main_model = model
            # 实时更新 UI 上的主模型显示
            if hasattr(self, 'main_model_label'):
                self.main_model_label.setText(f"主模型：{model}")
            QMessageBox.information(self, "已选择", f"主模型已切换为：{model}")

    def select_aux_model(self):
        items = ["GPT-4o-mini（推荐，低成本）", "DeepSeek 低成本轻量模型", "Qwen-Turbo / 其他低成本AI"]
        sel, ok = QInputDialog.getItem(self, "选择辅助模型", "辅助模型：", items, current=0, editable=False)
        if ok and sel:
            # 仅演示：将选择保存为 weather_model
            mapping = {
                items[0]: 'gpt-4o-mini',
                items[1]: 'deepseek-lite',
                items[2]: 'qwen-turbo'
            }
            self.ai_api.weather_model = mapping.get(sel, 'gpt-4o-mini')
            QMessageBox.information(self, "已选择", f"辅助模型已设置为：{sel}")

    def set_user_avatar(self):
        image_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择用户头像",
            str(path_manager.assest_dir),
            "图片文件 (*.jpg *.jpeg *.png *.bmp *.webp)"
        )
        if image_path:
            self.user_avatar_path = Path(image_path)
            # self.log_box.append(f"[设置] 用户头像已更新：{self.user_avatar_path}")
            # QMessageBox.information(self, "已保存", "用户头像已设置成功。")

    def clear_local_logs(self):
        ok = QMessageBox.question(self, "清除日志", "确定要清除本地日志文件并清空界面日志吗？", QMessageBox.Yes | QMessageBox.No)
        if ok == QMessageBox.Yes:
            # 清空显示日志
            self.log_box.clear()
            # 删除 upload_dir 下的 .log 文件（若有）
            try:
                for p in self.upload_dir.glob('*.log'):
                    p.unlink()
                QMessageBox.information(self, "完成", "本地日志已清除。")
            except Exception as e:
                QMessageBox.warning(self, "部分清除失败", f"清除日志时发生错误：{e}")

    def configure_encryption(self):
        items = ["关闭", "对称加密(AES)", "不对称加密(RSA)" ]
        sel, ok = QInputDialog.getItem(self, "数据加密配置", "请选择加密方式：", items, current=0, editable=False)
        if ok and sel:
            # 这里只是保存一个演示属性
            setattr(self, 'data_encryption', sel)
            QMessageBox.information(self, "已保存", f"数据加密配置：{sel}")

    def manage_account(self):
        # 简易账户管理：登录或注册（使用 interfaces.DatabaseAPI 的 mock）
        db = DatabaseAPI()
        choice, ok = QInputDialog.getItem(self, "账户", "请选择操作：", ["登录", "注册"], editable=False)
        if not ok:
            return
        username, ok1 = QInputDialog.getText(self, "账户", "用户名：")
        if not ok1:
            return
        password, ok2 = QInputDialog.getText(self, "账户", "密码：")
        if not ok2:
            return
        if choice == "登录":
            if db.check_login(username, password):
                QMessageBox.information(self, "登录成功", f"欢迎，{username}。")
            else:
                QMessageBox.warning(self, "登录失败", "用户名或密码错误。")
        else:
            if db.register_user(username, password):
                QMessageBox.information(self, "注册成功", "账户已创建，请使用登录进行验证。")
            else:
                QMessageBox.warning(self, "注册失败", "无法创建账户，请检查输入。")

    def force_reset_lower(self):
        ok = QMessageBox.question(self, "强制重置下位机", "确认发送重置命令到下位机？", QMessageBox.Yes | QMessageBox.No)
        if ok == QMessageBox.Yes:
            # 若 stm32_api 实现了 reset 方法则调用，否则只记录日志
            if hasattr(self.stm32_api, 'reset'):
                try:
                    self.stm32_api.reset()
                    self.log_box.append("[操作] 已向下位机发送重置命令。")
                except Exception as e:
                    QMessageBox.warning(self, "失败", f"发送重置命令失败：{e}")
            else:
                self.log_box.append("[操作] (模拟) 已向下位机发送重置命令。")
                QMessageBox.information(self, "已发送", "已模拟发送重置命令（下位机接口未实现）。")

    def stop_all_motors(self):
        ok = QMessageBox.question(self, "停止电机", "确认立刻停止所有电机动作？", QMessageBox.Yes | QMessageBox.No)
        if ok == QMessageBox.Yes:
            # 若 bt_api 或 stm32_api 提供停止接口则调用
            done = False
            for api in (self.bt_api, self.stm32_api):
                if hasattr(api, 'stop_all'):
                    try:
                        api.stop_all()
                        done = True
                    except Exception:
                        pass
            if done:
                self.log_box.append("[安全] 已向设备发送停止命令。")
                QMessageBox.information(self, "完成", "已发送停止命令。")
            else:
                self.log_box.append("[安全] (模拟) 已执行停止所有电机动作。")
                QMessageBox.information(self, "已执行", "模拟停止所有电机动作（接口未实现）。")

    def show_device_serial(self):
        # 展示下位机的串口信息或序列号
        serial_info = getattr(self.stm32_api, 'serial_port', None) or getattr(self.stm32_api, 'device_id', None) or '未知'
        QMessageBox.information(self, "设备序列号", f"下位机串口 / 标识：{serial_info}")

    def show_performance(self):
        # 显示简单性能数据（电池与锌肥百分比）
        batt = self.stm32_api.get_battery_level()
        zinc = self.stm32_api.get_zinc_level()
        QMessageBox.information(self, "性能", f"电池剩余：{batt}%\n锌肥余量：{zinc}%")

