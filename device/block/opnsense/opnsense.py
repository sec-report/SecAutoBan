import sys
import json
import time
import requests
import websocket
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
    if message["method"] == "blockIp":
        customize_print("[+] 封禁IP: " + message["data"]["ip"])
        block_ip(message["data"]["ip"])
        return
    if message["method"] == "unblockIp":
        customize_print("[+] 解禁IP: " + message["data"]["ip"])
        unblock_ip(message["data"]["ip"])
        return
    if message["method"] == "sync":
        global sync_flag
        if sync_flag:
            customize_print("[-] 已有线程进行全量封禁IP库同步，跳过本次请求")
            return
        sync_flag = True
        customize_print("[+] 同步全量封禁IP库: " + str(len(message["data"]["ips"])) + "个")
        for deviceIp in get_all_ips():
            if deviceIp not in message["data"]["ips"]:
                unblock_ip(deviceIp)
        for ip in message["data"]["ips"]:
            block_ip(ip)
        customize_print("[+] 同步全量封禁IP库完成")
        sync_flag = False
        return


def on_error(w, error):
    customize_print("Error:" + str(error))


def on_close(w, code, message):
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
            "type": "blockDevice"
        }
    }
    w.send(key + iv + aes_cfb_encrypt(key, iv, json.dumps(send_data).encode()))


def connect_websocket():
    ws.run_forever(skip_utf8_validation=True)


def block_ip(ip):
    if check_exist_ip(ip):
        return
    url = 
    post_data = {
        "address": ip
    }
    r = requests.post(opnsense_url + "/api/firewall/alias_util/add/" + opnsense_alias_name, auth=(api_key, api_secret), json=post_data, timeout=60)
    if r.status_code != 200:
        customize_print("[-] 添加封禁失败")
        return
    if r.json["status"] != "done":
        customize_print("[-] 添加封禁失败")


def unblock_ip(ip):
    url = opnsense_url + "/api/firewall/alias_util/delete/" + opnsense_alias_name
    post_data = {
        "address": ip
    }
    r = requests.post(url, auth=(api_key, api_secret), json=post_data, timeout=60)
    if r.status_code != 200:
        customize_print("[-] 解除封禁失败")
        return
    if r.json["status"] != "done":
        customize_print("[-] 解除封禁失败")


def get_all_ips() -> list:
    ip_list = []
    url = opnsense_url + "/api/firewall/alias_util/list/" + opnsense_alias_name
    r = requests.get(url, auth=(api_key, api_secret), timeout=60)
    if r.status_code != 200:
        customize_print("[-] 获取全量IP失败")
        return
    for i in r.json()["rows"]:
        ip_list.append(i["ip"])
    return ip_list


def check_exist_ip(ip) -> bool:
    if ip in get_all_ips():
        return True
    return False


if __name__ == "__main__":
    server_ip = "127.0.0.1"
    server_port = 8080
    sk = "sk-xxx"
    opnsense_url = "http://xxx.xxx.xxx.xxx"
    opnsense_alias_name = "sec_auto_ban"
    opnsense_api_key = 'xxx'
    opnsense_api_secret = 'xxx'
    ws = websocket.WebSocketApp(
        "ws://" + server_ip + ":" + str(server_port) + "/device",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    sync_flag = False
    is_login = False
    pool = ThreadPool(processes=2)
    pool.apply_async(connect_websocket)
    pool.close()
    pool.join()
