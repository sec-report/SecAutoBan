import sqlite3
from SecAutoBan import SecAutoBan
from scapy.all import sniff, send
from scapy.layers.inet6 import IPv6
from scapy.layers.inet import TCP, IP
from multiprocessing.pool import ThreadPool


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
        sec_auto_ban.print("[+] 阻断连接：" + src_ip + ":" + str(src_port) + " -> " + dst_ip + ":" + str(dst_port))
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
            sec_auto_ban.print("[-] 阻断失败: Error: " + str(e))
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
    sql_conn = sqlite3.connect(db_name)
    cursor = sql_conn.cursor().execute("SELECT ip from IP")
    for row in cursor:
        db_ip_list.append(row[0])
    sql_conn.close()
    return db_ip_list


def block_ip(ip):
    if check_exist_ip(ip):
        return
    global ban_ip_list
    ban_ip_list.append(ip)
    sql_conn = sqlite3.connect(db_name)
    sql_conn.execute('INSERT INTO IP (ip) VALUES (?)', (ip,))
    sql_conn.commit()
    sql_conn.close()


def unblock_ip(ip):
    global ban_ip_list
    ban_ip_list.remove(ip)
    sql_conn = sqlite3.connect(db_name)
    sql_conn.execute('DELETE FROM IP WHERE ip=?', (ip,))
    sql_conn.commit()
    sql_conn.close()


def get_all_block_ip() -> list:
    return ban_ip_list


def check_exist_ip(ip) -> bool:
    return ip in ban_ip_list


def run_sniff():
    sql_conn = sqlite3.connect(db_name)
    sql_conn.execute('''
        CREATE TABLE IF NOT EXISTS IP (
            ip TEXT,
            CONSTRAINT idx_ip UNIQUE (ip)
        )
    ''')
    sql_conn.close()
    global ban_ip_list
    ban_ip_list.clear()
    ban_ip_list += get_db_all_ip()
    sniff(
        iface=sniff_iface,
        prn=send_reset(reset_iface),
        lfilter=is_filter()
    )


if __name__ == "__main__":
    sniff_iface = "eth0"
    reset_iface = "eth1"
    db_name = "block_ip.db"
    ban_ip_list = []
    sec_auto_ban = SecAutoBan(
        server_ip="127.0.0.1",
        server_port=8000,
        sk="sk-*****",
        client_type="block",
        block_ip = block_ip,
        unblock_ip = unblock_ip,
        get_all_block_ip= get_all_block_ip
    )
    pool = ThreadPool(processes=1)
    pool.apply_async(run_sniff)
    pool.close()
    pool.join()
    sec_auto_ban.run()
