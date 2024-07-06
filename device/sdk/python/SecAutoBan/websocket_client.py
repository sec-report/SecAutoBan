import json
import time
import websocket
from . import util

class WebSocketClient:
    init = False
    is_login = False
    sync_flag = False
    
    def __init__(self, server_ip: str, server_port: int, sk: str, client_type: str, block_ip=None, unblock_ip=None, get_all_block_ip=None):
        self.server_ip = server_ip
        self.server_port = server_port
        self.sk = sk
        if client_type not in ["alarm", "block"]:
            util.print("[-] 初始化失败: 未知的模块类型" + client_type)
            return
        if client_type == "block":
            if block_ip is None or unblock_ip is None:
                util.print("[-] 初始化失败: 未实现封禁函数")
                return
            self.block_ip = block_ip
            self.unblock_ip = unblock_ip
            self.get_all_block_ip = get_all_block_ip
        self.client_type = client_type
        self.ws = websocket.WebSocketApp(
            "ws://" + server_ip + ":" + str(server_port) + "/device",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        self.init =True


    def on_message(self, w, message):
        if len(message) <= 16:
            return
        message = json.loads(util.aes_cfb_decrypt(self.sk[3:].encode(), message[0:16], message[16:]).decode())
        if message["method"] == "login":
            self.is_login = True
            util.print("[+] 登录成功，设备名称: " + message["data"]["deviceName"])
        if self.type == "block":
            if message["method"] == "blockIp":
                util.print("[+] 封禁IP: " + message["data"]["ip"])
                self.block_ip(message["data"]["ip"])
                return
            if message["method"] == "unblockIp":
                util.print("[+] 解禁IP: " + message["data"]["ip"])
                self.unblock_ip(message["data"]["ip"])
                return
            if message["method"] == "sync":
                if self.get_all_block_ip is None:
                    util.print("[-] 全量封禁IP同步失败：未实现获取全部封禁IP函数，跳过本次请求")
                    return
                if self.sync_flag:
                    util.print("[-] 全量封禁IP同步失败：已有线程进行全量封禁IP库同步，跳过本次请求")
                    return
                self.sync_flag = True
                util.print("[+] 同步全量封禁IP库: " + str(len(message["data"]["ips"])) + "个")
                for deviceIp in self.get_all_block_ip():
                    if deviceIp not in message["data"]["ips"]:
                        self.unblock_ip(deviceIp)
                for ip in message["data"]["ips"]:
                    self.block_ip(ip)
                util.print("[+] 同步全量封禁IP库完成")
                self.sync_flag = False
                return    

    def on_error(self, w, error):
        util.print("Error: " + str(error))

    def on_close(self, w, code, message):
        self.is_login = False
        util.print("[-] 服务器连接异常断开")
        util.print("[*] 5秒后自动重连")
        time.sleep(5)
        self.connect()

    def on_open(self, w):
        util.print("[+] 连接服务器")
        key = util.random_bytes()
        iv = util.random_bytes()
        send_data = {
            "method": "login",
            "data": {
                "key": self.sk,
            }
        }
        if self.client_type == "alarm":
            send_data["data"]["type"] = "alarmDevice"
        elif self.client_type == "block":
            send_data["data"]["type"] = "blockDevice"
        self.ws.send(key + iv + util.aes_cfb_encrypt(key, iv, json.dumps(send_data).encode()))

    def connect(self):
        if not self.init:
            return
        self.ws.run_forever(skip_utf8_validation=True)

    def send_alarm(self, ip: str, origin: str):
        if self.client_type == "block":
            util.print("[-] 封禁模块无法发送告警数据")
            return
        if not self.is_login:
            util.print("[-] 未登录成功，无法发送数据")
            return
        send_data = {
            "method": "alarmIp",
            "data": {
                "ip": ip,
                "origin": origin
            }
        }
        iv = util.random_bytes()
        util.print("[+] 发送告警IP: " + ip + "\t" + origin)
        self.ws.send(iv + util.aes_cfb_encrypt(self.sk[3:].encode(), iv, json.dumps(send_data).encode()))
