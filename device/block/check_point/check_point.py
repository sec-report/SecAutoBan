import time
import signal
import requests
from SecAutoBan import SecAutoBan
from multiprocessing.pool import ThreadPool
requests.packages.urllib3.disable_warnings()


def signal_handler(signal, frame):
    sec_auto_ban.print("[+] 注销Session")
    publish()
    logout()
    exit()


def login():
    post_json = {
        "user": check_point_conf["username"],
        "password": check_point_conf["password"],
    }
    r = requests.post(check_point_conf["url"] + "/web_api/login", json=post_json, verify=False)
    if r.status_code == 200 and "sid" in r.json():
        sec_auto_ban.print("[+] 防火墙登录成功")
    else:
        sec_auto_ban.print("[-] 防火墙登录失败")
        exit()
    global check_point_session_id
    check_point_session_id = r.json()["sid"]


def discard():
    header = {
        "X-chkp-sid": check_point_session_id
    }
    requests.post(check_point_conf["url"] + "/web_api/discard", json={}, headers=header, verify=False)


def publish():
    header = {
        "X-chkp-sid": check_point_session_id
    }
    r = requests.post(check_point_conf["url"] + "/web_api/publish", json={}, headers=header, verify=False)
    if "task-id" not in r.json():
        sec_auto_ban.print("[-] 推送失败，回退session")
        discard()


def logout():
    header = {
        "X-chkp-sid": check_point_session_id
    }
    requests.post(check_point_conf["url"] + "/web_api/logout", json={}, headers=header, verify=False)


def keepalive():
    time.sleep(60)
    header = {
        "X-chkp-sid": check_point_session_id
    }
    r = requests.post(check_point_conf["url"] + "/web_api/keepalive", json={}, headers=header, verify=False)
    if r.status_code != 200:
        login()
    keepalive()


def check_host(ip: str) -> str:
    post_json = {
        "filter": ip
    }
    header = {
        "X-chkp-sid": check_point_session_id
    }
    r = requests.post(check_point_conf["url"] + "/web_api/show-hosts", json=post_json, headers=header, verify=False)
    if "total" in r.json():
        if r.json()["total"] == 0:
            return ""
        return r.json()["objects"][0]["uid"]
    return ""


def get_host_uid(ip: str) -> str:
    uid = check_host(ip)
    if len(uid) != 0:
        return uid
    post_json = {
        "name": "block_" + ip,
        "ip-address": ip
    }
    header = {
        "X-chkp-sid": check_point_session_id
    }
    r = requests.post(check_point_conf["url"] + "/web_api/add-host", json=post_json, headers=header, verify=False)
    return r.json()["uid"]


def block_ip(ip):
    if check_exist_ip(ip):
        return
    host_uid = get_host_uid(ip)
    if len(host_uid) == 0:
        sec_auto_ban.print("[-] IP: " + ip + " 添加失败")
    post_json = {
        "name": check_point_conf["group_name"],
        "members": {
            "add": host_uid
        },
        "details-level": "uid"
    }
    header = {
        "X-chkp-sid": check_point_session_id
    }
    requests.post(check_point_conf["url"] + "/web_api/set-group", json=post_json, headers=header, verify=False)
    publish()
    

def unblock_ip(ip):
    if not check_exist_ip(ip):
        return
    host_uid = get_host_uid(ip)
    if len(host_uid) == 0:
        sec_auto_ban.print("[-] IP: " + ip + " 删除失败")
    post_json = {
        "name": check_point_conf["group_name"],
        "members": {
            "remove": host_uid
        },
    }
    header = {
        "X-chkp-sid": check_point_session_id
    }
    requests.post(check_point_conf["url"] + "/web_api/set-group", json=post_json, headers=header, verify=False)
    publish()


def get_all_block_ip() -> list:
    post_json = {
        "name": check_point_conf["group_name"]
    }
    header = {
        "X-chkp-sid": check_point_session_id
    }
    r = requests.post(check_point_conf["url"] + "/web_api/show-group", json=post_json, headers=header, verify=False)
    return [i["ipv4-address"]for i in r.json()["members"]]


def check_exist_ip(ip) -> bool:
    return ip in get_all_block_ip()


if __name__ == "__main__":
    check_point_session_id = ""
    check_point_conf = {
        "url": "https://xxx.xxx.xxx.xxx",
        "username": "admin",
        "password": "",
        "group_name": "sec_auto_ban"
    }
    sec_auto_ban = SecAutoBan(
        server_ip="127.0.0.1",
        server_port=80,
        sk="sk-*****",
        client_type="block",
        block_ip = block_ip,
        unblock_ip = unblock_ip,
        get_all_block_ip= get_all_block_ip
    )
    pool = ThreadPool(processes=1)
    login()
    pool.apply_async(keepalive)
    signal.signal(signal.SIGINT, signal_handler)
    sec_auto_ban.run()
