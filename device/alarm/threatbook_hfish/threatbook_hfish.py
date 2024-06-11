import sys
import json
import time
import requests
import websocket
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from multiprocessing.pool import ThreadPool
requests.packages.urllib3.disable_warnings()

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


def analysis_alarm():
    ip_list = []
    while True:
        time.sleep(5)
        post_data = {
            "start_time": 0,
            "end_time": 0,
            "page_no": 1,
            "page_size": 20,
            "intranet": 0,
            "threat_label": [],
            "client_id": [],
            "service_name": [],
            "info_confirm": "0"
        }
        try:
            r = requests.post(hfish_url + "/api/v1/attack/detail?api_key=" + hfish_api_key, json=post_data, verify=False)
        except Exception as e:
            customize_print("[-] 获取蜜罐数据失败")
            print("[-] Error: " + str(e))
            continue
        if r.status_code != 200:
            customize_print("[-] 获取蜜罐数据失败")
            continue
        if r.json()["verbose_msg"] != "成功":
            customize_print("[-] 获取蜜罐数据失败")
            continue
        for i in r.json()["data"]["detail_list"]:
            if i["attack_ip"] not in ip_list:
                send_alarm_ip(i["attack_ip"], "攻击" + i["service_name"])
                ip_list.append(i["attack_ip"])
                if len(ip_list) > 10000:
                    ip_list.pop(0)


if __name__ == "__main__":
    server_ip = "127.0.0.1"
    server_port = 8080
    sk = "sk-xxx"
    hfish_url = "https://xxx.xxx.xxx.xxx:4433"
    hfish_api_key = "xxx"
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
