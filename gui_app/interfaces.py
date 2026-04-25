class AI_API:
    """内部特定训练AI的交互接口 (接入大模型API)"""
    def __init__(self, main_model="deepseek-v3.2", weather_model="gpt-4o-mini"):
        # 默认采用 OpenAI 兼容格式的接口。如果是特定的平台(如通义、Kimi、DeepSeek等)请修改对应的 api_url 和 model 名
        self.api_url = "https://vg.v1api.cc/v1/chat/completions"
        self.api_key = "sk-TrWwKVuKA2YS5RckVJnWOH4T2XgoyL8m6j9qoMdewz3DVoEe"
        self.main_model = main_model
        self.weather_model = weather_model
        self.model = self.main_model

    def _weather_keywords(self):
        return (
            "天气", "气温", "温度", "湿度", "降雨", "下雨", "下雪", "刮风",
            "风速", "气压", "预报", "晴", "阴", "多云", "雷阵雨", "台风"
        )

    def is_weather_question(self, message: str) -> bool:
        return any(keyword in message for keyword in self._weather_keywords())

    def _chat_with_model_name(self, message: str, model_name: str, system_prompt: str) -> str:
        import requests

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ]
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            return f"【API 请求失败】状态码: {response.status_code}\n详情: {response.text}"
        except Exception as e:
            return f"【请求异常】无法连接到 AI 服务器。请检查网络或第三方提供商地址，错误信息: {str(e)}"

    def chat_with_model(self, message: str) -> str:
        system_prompt = (
            "你是苗健谷满仓项目的智能农业AI专家，专门负责解答关于玉米幼苗剪切、锌肥喷洒相关的专业问题。"
            "当用户询问你是谁时，请回答以上你的身份，且语言风格必须柔和，不许顶撞用户，即使用户是错的你也要柔和地解释，"
            "如果必要则做出让步，此外，如果用户的设备出现问题，询问你小车故障问题，你也需要根据用户的描述进行推理判断并尝试给出解决办法，"
            "切记，每次回复解决办法时，必须在文本的最后一段提示用户以下内容：\"联系维修人员或者去线下门店找专业维修人员进行维修\"，"
            "以下是产品信息：玉米苗期割苗助产与精准喷锌肥机械臂小车，是一款集成自主行走、视觉识别与机械臂作业的小型智能田间装备。"
            "整车采用轻量化履带底盘（重约8kg），搭载多自由度折叠机械臂与多功能复合末端执行器，可一次性完成玉米幼苗标准化割苗控旺与锌肥定点定量喷施。"
            "系统基于机器视觉与多传感器融合技术，通过YOLO目标检测、分水岭分割及霍夫圆变换算法实现幼苗苗心亚像素级精准定位，定位偏差≤10mm；"
            "配合霍尔编码器+PID闭环控制，割苗高度调节精度±5mm，单株作业耗时≤3s。太阳能蓄电池驱动，适配行距30cm以上地块，"
            "割苗准确率≥98%，喷施均匀度≥95%，锌肥利用率提升30%以上，作业效率达人工的4—10倍，设备成本控制在1500元左右，"
            "为玉米苗期精准化、轻简化管理提供低成本解决方案。"
        )
        return self._chat_with_model_name(message, self.main_model, system_prompt)

    def chat_with_weather_model(self, message: str) -> str:
        weather_prompt = (
            "你是一个低成本天气助手，专门回答天气、气温、降雨、风速、湿度、预报等问题。"
            "回答要简洁、准确、易懂；如果缺少实时数据，要明确说明无法获取实时天气。"
        )
        return self._chat_with_model_name(message, self.weather_model, weather_prompt)

    def chat_auto(self, message: str):
        if self.is_weather_question(message):
            return self.chat_with_weather_model(message), "天气辅助模型"
        return self.chat_with_model(message), "主模型"

class DatabaseAPI:
    """SQL数据库接口 (留存逻辑但不强连接)"""
    # 临时使用内存字典模拟数据库，方便测试注册和登录
    _mock_db = {"admin": "123"}

    def __init__(self):
        self.db_host = "localhost"
        self.table = "users"
        self.connected = False

    def check_login(self, username, password) -> bool:
        # TODO: Implement explicit SQL Connector checks here
        if username in self._mock_db and self._mock_db[username] == password:
            return True
        return False

    def register_user(self, username, password) -> bool:
        # TODO: Implement SQL INSERT INTO users here
        if not username or not password:
            return False
        self._mock_db[username] = password
        return True

class BluetoothAPI:
    """与手机 (iOS / HarmonyOS / 安卓) 通讯控制的接口"""
    def __init__(self):
        self.bt_mac = "XX:XX:XX:XX:XX:XX"
        self.port = 1
        
    def connect_app(self):
        # Bluetooth sockets / pybluez logic
        pass

class STM32API:
    """与 STM32407V1T6 下位机通讯接口 (UART 或 CAN)"""
    def __init__(self):
        self.serial_port = "COM3"
        self.baudrate = 115200

    def get_battery_level(self):
        # TODO: Read from Serial buffer (e.g. 0x01 command -> Hex battery string)
        return 99

    def get_zinc_level(self):
        # TODO: Read zinc tank sensor levels via ADC values sent from STM32
        return 20

class CameraAPI:
    """香橙派摄像头图像接收与转发 (TCP / UDP / HTTP Stream)"""
    def __init__(self):
        self.stream_url = "http://orange-pi.local:8080/video"

    def fetch_frame(self):
        # TODO: OpenCV VideoCapture
        pass