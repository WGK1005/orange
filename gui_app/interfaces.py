class AI_API:
    """内部特定训练AI的交互接口 (接入大模型API)"""
    def __init__(self):
        # 默认采用 OpenAI 兼容格式的接口。如果是特定的平台(如通义、Kimi、DeepSeek等)请修改对应的 api_url 和 model 名
        self.api_url = "https://vg.v1api.cc/v1/chat/completions"
        self.api_key = "sk-TrWwKVuKA2YS5RckVJnWOH4T2XgoyL8m6j9qoMdewz3DVoEe"
        self.model = "gpt-3.5-turbo"

    def chat_with_model(self, message: str) -> str:
        import requests
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "你是一个智能农业专家AI，负责解答关于玉米幼苗剪切、锌肥喷洒以及农业机器人巡检相关的专业问题。"},
                {"role": "user", "content": message}
            ]
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=15)
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"【API 请求失败】状态码: {response.status_code}\n详情: {response.text}"
        except Exception as e:
            return f"【请求异常】无法连接到 AI 服务器。请检查网络或第三方提供商地址，错误信息: {str(e)}"

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