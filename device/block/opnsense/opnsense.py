import requests
from SecAutoBan import SecAutoBan


def block_ip(ip):
    if check_exist_ip(ip):
        return
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


def get_all_block_ip() -> list:
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
    return ip in get_all_block_ip()


if __name__ == "__main__":
    opnsense_url = "http://xxx.xxx.xxx.xxx"
    opnsense_api_key = 'xxx'
    opnsense_api_secret = 'xxx'
    opnsense_alias_name = "sec_auto_ban"
    sec_auto_ban = SecAutoBan(
        server_ip="127.0.0.1",
        server_port=8000,
        sk="sk-*****",
        client_type="block",
        block_ip = block_ip,
        unblock_ip = unblock_ip,
        get_all_block_ip= get_all_block_ip
    )
    sec_auto_ban.run()
