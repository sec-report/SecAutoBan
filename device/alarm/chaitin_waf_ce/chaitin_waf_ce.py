import sys
import jwt
import json
import time
import datetime
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


def get_header():
    header = {}
    if len(chaitin_waf_login_conf["jwt-secret"]) == 0:
        header["Authorization"] = "Bearer " + chaitin_waf_login_conf["bearer"]
    else:
        t = int((datetime.datetime.now()+datetime.timedelta(days=7)).timestamp())
        jwt_payload = {
            "uid": 1,
            "pwd": True,
            "tfa": False,
            "ver": 1,
            "iss": "chaitin",
            "exp": t,
            "iat": t
        }
        token = jwt.encode(jwt_payload, chaitin_waf_login_conf["jwt-secret"], algorithm='HS256')
        header["Authorization"] = "Bearer " + token
    return header


def analysis_alarm():
    event_id_list = []
    while True:
        time.sleep(5)
        try:
            r = requests.get(
                chaitin_waf_url + "/api/open/records?page=1&page_size=20&ip=&url=&port=&host=&attack_type=&action=1",
                headers=get_header(),
                verify=False
            )
        except Exception as e:
            customize_print("[-] WAF连接失败, Error: " + str(e))
            continue
        if r.status_code != 200:
            if r.status_code == 401:
                customize_print("[-] WAF登录失败")
                continue
            customize_print("[-] WAF连接失败")
            continue
        for i in r.json()["data"]["data"]:
            if i["event_id"] not in event_id_list:
                send_alarm_ip(i["src_ip"], "攻击资产：" + i["host"] + " " + i["reason"])
                event_id_list.append(i["event_id"])
                if len(event_id_list) > 10000:
                    event_id_list.pop(0)


if __name__ == "__main__":
    server_ip = "127.0.0.1"
    server_port = 8080
    sk = "sk-xxx"
    chaitin_waf_url = "https://xxx.xxx.xxx.xxx:9443"
    chaitin_waf_login_conf = {
        "jwt-secret": "",
        "bearer": "xxx.xxx.xxx"
    }
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
    analysis_alarm()
    pool.close()
    pool.join()
