import sys
import json
import time
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


# 实现设备封禁函数
def block_ip(ip):
    pass


# 实现设备解封函数
def unblock_ip(ip):
    pass


if __name__ == "__main__":
    server_ip = "127.0.0.1"
    server_port = 8080
    sk = "sk-xxx"
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
