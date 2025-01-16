import time
import requests
import urllib.parse
from SecAutoBan import SecAutoBan
from multiprocessing.pool import ThreadPool

def push():
    while True:
        time.sleep(60)
        global ban_ip_list
        if len(ban_ip_list) == 0:
            continue
        post_data = {
            "msgtype": "text",
            "text":{
                "content":"封禁IP如下：\n" + "\n".join(ban_ip_list)
    	   }
        }
        ban_ip_list.clear()
        sec_auto_ban.print("[+] 推送消息: " + post_data["text"]["content"])
        try:
        	response= requests.post(webhook + hook_key, json=post_data, timeout=60)
        	response.raise_for_status()
        except requests.exceptions.RequestException as e:
        	sec_auto_ban.print(f"[+] 推送消息失败: {e}")

def block_ip(ip):
    if check_exist_ip(ip):
        return
    global ban_ip_list
    ban_ip_list.append(ip)


def unblock_ip(ip):
    global ban_ip_list
    if check_exist_ip(ip):
        ban_ip_list.remove(ip)


def check_exist_ip(ip) -> bool:
    return ip in ban_ip_list


if __name__ == "__main__":
    webhook = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key="
    hook_key = "aaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaa"
    ban_ip_list = []
    sec_auto_ban = SecAutoBan(
        server_ip="127.0.0.1",
        server_port=80,
        sk="sk-*****",
        client_type="block",
        block_ip = block_ip,
        unblock_ip = unblock_ip,
    )
    pool = ThreadPool(processes=1)
    pool.apply_async(push)
    pool.close()
    sec_auto_ban.run()
    pool.join()
