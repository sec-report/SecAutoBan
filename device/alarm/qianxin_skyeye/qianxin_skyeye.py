import sys
import json
import time
import websocket
import ipaddress
import socketserver
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from multiprocessing.pool import ThreadPool


def customize_print(s: str):
    sys.stdout.write(time.strftime("%Y-%m-%d %H:%M:%S\t", time.localtime()) + s + "\n")
    sys.stdout.flush()


def aes_cfb_encrypt(key: bytes, iv: bytes, plain_content: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=128)
    return cipher.encrypt(plain_content)


def aes_cfb_decrypt(key: bytes, iv: bytes, cipher_content: bytes) -> bytes:
    cipher = AES.new(key, AES.MODE_CFB, iv, segment_size=128)
    return cipher.decrypt(cipher_content)


def on_message(w, message):
    if len(message) <= 16:
        return
    message = json.loads(aes_cfb_decrypt(sk[3:].encode(), message[0:16], message[16:]).decode())
    if message["method"] == "login":
        global is_login
        is_login = True
        customize_print("[+] 登录成功，设备名称: " + message["data"]["deviceName"])
        return


def on_error(w, error):
    customize_print("Error:" + str(error))


def on_close(w, code, message):
    global is_login
    is_login = False
    customize_print("[-] 服务器连接异常断开")
    customize_print("[*] 5秒后自动重连")
    time.sleep(5)
    connect_websocket()


def on_open(w):
    customize_print("[+] 连接服务器")
    key = get_random_bytes(16)
    iv = get_random_bytes(16)
    send_data = {
        "method": "login",
        "data": {
            "key": sk,
            "type": "alarmDevice"
        }
    }
    w.send(key + iv + aes_cfb_encrypt(key, iv, json.dumps(send_data).encode()))


def connect_websocket():
    ws.run_forever(skip_utf8_validation=True)


def send_alarm_ip(ip: str, origin: str):
    if is_login is False:
        customize_print("[-] 未登录成功，无法发送数据")
        return
    send_data = {
        "method": "alarmIp",
        "data": {
            "ip": ip,
            "origin": origin
        }
    }
    iv = get_random_bytes(16)
    customize_print("[+] 发送告警IP: " + ip + "\t" + origin)
    ws.send(iv + aes_cfb_encrypt(sk[3:].encode(), iv, json.dumps(send_data).encode()))


def is_lan(ip: str) -> bool:
    if bypass_lan:
        return ipaddress.ip_address(ip).is_private
    return False


class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def handle(self):
        data = self.request[0]
        message = data.decode('utf-8')
        messages = message.split('\n')
        for msg in messages:
            if msg == "":
                continue
            msg = json.loads(msg.split("|!alarm|!")[1])
            sip = msg["attack_sip"]
            if sip == "":
                continue
            if is_lan(sip):
                continue
            origin = "攻击" + msg["alarm_sip"] + ": [" + msg["type"] + "]" + msg["vuln_type"]
            send_alarm_ip(sip, origin)


def analysis_alarm():
    with socketserver.ThreadingUDPServer(("0.0.0.0", listen_syslog_udp_port), SyslogUDPHandler) as server:
        customize_print("[+] 监听SysLog端口: " + str(listen_syslog_udp_port) + "/UDP")
        server.serve_forever()


if __name__ == "__main__":
    server_ip = "127.0.0.1"
    server_port = 8080
    sk = "sk-xxx"
    listen_syslog_udp_port = 547
    bypass_lan = True  # 过滤内网攻击，True 开启 | False 关闭
    ws = websocket.WebSocketApp(
        "ws://" + server_ip + ":" + str(server_port) + "/device",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    is_login = False
    pool = ThreadPool(processes=2)
    pool.apply_async(connect_websocket)
    pool.apply_async(analysis_alarm)
    pool.close()
    pool.join()
