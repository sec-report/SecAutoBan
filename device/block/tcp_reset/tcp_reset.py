import sys
import json
import time
import random
import sqlite3
import websocket
from Crypto.Cipher import AES
from scapy.all import sniff, send
from scapy.layers.inet6 import IPv6
from scapy.layers.inet import TCP, IP
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


def get_ip(p):
    src_ip = ""
    dst_ip = ""
    if p.haslayer(IP):
        src_ip = p[IP].src
        dst_ip = p[IP].dst
    if p.haslayer(IPv6):
        src_ip = p[IPv6].src
        dst_ip = p[IPv6].dst
    return src_ip, dst_ip


def send_reset(iface, seq_jitter=0, default_window_size=2052):
    def f(p):
        src_ip, dst_ip = get_ip(p)
        src_port = p[TCP].sport
        dst_port = p[TCP].dport
        seq = p[TCP].seq
        ack = p[TCP].ack
        customize_print("[+] 阻断连接：" + src_ip + ":" + str(src_port) + " -> " + dst_ip + ":" + str(dst_port))
        jitter = random.randint(max(-seq_jitter, -seq), seq_jitter)
        rst_seq = ack + jitter
        try:
            if p.haslayer(IP):
                p = IP(src=dst_ip, dst=src_ip) / TCP(sport=dst_port, dport=src_port, flags="R", window=default_window_size, seq=rst_seq)
                send(p, verbose=0, iface=iface)
                return
            if p.haslayer(IPv6):
                p = IPv6(src=dst_ip, dst=src_ip) / TCP(sport=dst_port, dport=src_port, flags="R", window=default_window_size, seq=rst_seq)
                send(p, verbose=0, iface=iface)
                return
        except Exception as e:
            customize_print("[-] 阻断失败: Error: " + str(e))
    return f


def is_filter():
    def f(p):
        if not p.haslayer(TCP):
            return False
        src_ip, dst_ip = get_ip(p)
        return src_ip in ban_ip_list or dst_ip in ban_ip_list
    return f


def get_db_all_ip():
    db_ip_list = []
    cursor = sql_conn.cursor().execute("SELECT ip from IP")
    for row in cursor:
        db_ip_list.append(row[0])
    return db_ip_list


def block_ip(ip):
    if check_exist_ip(ip):
        return
    ban_ip_list.append(ip)
    sql_conn.execute('INSERT INTO IP (ip) VALUES (?)', (ip,))
    sql_conn.commit()


def unblock_ip(ip):
    ban_ip_list.remove(ip)
    sql_conn.execute('DELETE FROM IP WHERE ip=?', (ip,))
    sql_conn.commit()


def get_all_ips() -> list:
    return ban_ip_list


def check_exist_ip(ip) -> bool:
    return ip in ban_ip_list


def run_sniff():
    sql_conn.execute('''
        CREATE TABLE IF NOT EXISTS IP (
            ip TEXT,
            CONSTRAINT idx_ip UNIQUE (ip)
        )
    ''')
    global ban_ip_list
    ban_ip_list.clear()
    ban_ip_list += get_db_all_ip()
    sniff(
        iface=sniff_iface,
        prn=send_reset(reset_iface),
        lfilter=is_filter()
    )


if __name__ == "__main__":
    server_ip = "127.0.0.1"
    server_port = 8080
    sk = "sk-xxx"
    sniff_iface = "eth0"
    reset_iface = "eth1"
    ban_ip_list = []
    sql_conn = sqlite3.connect('block_ip.db')
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
    run_sniff()
    pool.close()
    pool.join()
