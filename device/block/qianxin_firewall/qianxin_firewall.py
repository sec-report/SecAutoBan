import requests
from SecAutoBan import SecAutoBan
requests.packages.urllib3.disable_warnings()


def login() -> str:
    url = fw_config["url"] + "/v1.0/login/"
    post_data = {
        "username": fw_config["username"],
        "password": fw_config["password"]
    }
    r = requests.post(url, json=post_data, timeout=60, verify=False)
    cookies = {
        "PHPSESSID" : r.cookies.get("PHPSESSID"),
        "token": r.json()["result"]["token"]
    }
    return cookies


def logout(cookies):
    url = fw_config["url"] + "/v1.0/out/"
    post_data = {
        "username": fw_config["username"]
    }
    requests.post(url, json=post_data, cookies=cookies, timeout=60, verify=False)
    

def block_ip(ip):
    cookies = login()
    if check_exist_ip(cookies, ip):
        return
    url = fw_config["url"] + "/v1.0/rest/"
    post_data = [{
        "head": {
            "function": "add_batch_blacklist",
            "module": "addr_blacklist"
        },
        "body": {
            "addr_blacklist_cp": {
                "batch_blacklist_list": [{
                    "ip": ip
                }]
            }
        }
    }]
    r = requests.post(url, json=post_data, cookies=cookies, timeout=60, verify=False)
    logout(cookies)
    if r.status_code != 200:
        customize_print("[-] 添加封禁失败")
        return
    if r.json()["head"]["error_code"] != 0:
        customize_print("[-] 添加封禁失败")
        return


def unblock_ip(ip):
    cookies = login()
    if not check_exist_ip(cookies, ip):
        return
    url = fw_config["url"] + "/v1.0/rest/"
    post_data = [{
        "head": {
            "function":"del_batch_blacklist",
            "module":"addr_blacklist"
        },
        "body": {
            "addr_blacklist_cp":{
                "batch_blacklist_list":[{
                    "ip": ip
                }]
            }
        }
    }]
    r = requests.post(url, json=post_data, cookies=cookies, timeout=60, verify=False)
    logout(cookies)
    if r.status_code != 200:
        customize_print("[-] 解除封禁失败")
        return
    if r.json()["head"]["error_code"] != 0:
        customize_print("[-] 解除封禁失败")


def get_all_block_ip() -> list:
    cookies = login()
    url = fw_config["url"] + "/v1.0/rest/"
    post_data = [{
        "head": {
            "function": "del_batch_blacklist_all",
            "module": "addr_blacklist"
        },
        "body": {}
    }]
    r = requests.post(url, json=post_data, cookies=cookies, timeout=60, verify=False)
    logout(cookies)
    return []


def check_exist_ip(cookies, ip) -> bool:
    url = fw_config["url"] + "/v1.0/rest/"
    post_data = [{
        "head": {
            "module": "addr_blacklist",
            "function": "show_batch_blacklist"
        },
        "body": {
            "addr_blacklist_cp": {
                "search_key": ip,
                "type": "time"
            }
        }
    }]
    r = requests.post(url, json=post_data, cookies=cookies, timeout=60, verify=False)
    return r.json()["head"]["total"] != 0


if __name__ == "__main__":
    fw_config = {
        "url": "https://xxx.xxx.xxx.xxx:8443",
        "username": "xxx",
        "password": "xxx",
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
    sec_auto_ban.run()
