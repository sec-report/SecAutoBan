import jwt
import time
import datetime
import requests
from SecAutoBan import SecAutoBan
requests.packages.urllib3.disable_warnings()


def password_login() -> str:
    r = requests.get(chaitin_waf_url + "/api/open/auth/csrf", verify=False)
    if r.status_code != 200:
        return ""
    post_data = {
        "csrf_token": r.json()["data"]["csrf_token"],
        "username": chaitin_waf_login_conf["username"],
        "password": chaitin_waf_login_conf["password"]
    }
    r = requests.post(chaitin_waf_url + "/api/open/auth/login", json=post_data, verify=False)
    if r.status_code != 200:
        return ""
    return r.json()["data"]["jwt"]


def get_header():
    header = {}
    if len(chaitin_waf_login_conf["jwt-secret"]) != 0:
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
    if len(chaitin_waf_login_conf["username"]) != 0:
        header["Authorization"] = "Bearer " + password_login()
        return header
    header["Authorization"] = "Bearer " + chaitin_waf_login_conf["bearer"]
    return header


def alarm_analysis(ws_client):
    event_id_list = []
    ip_list = []
    while True:
        time.sleep(5)
        try:
            r = requests.get(
                chaitin_waf_url + "/api/open/records?page=1&page_size=20&ip=&url=&port=&host=&attack_type=&action=1",
                headers=get_header(),
                verify=False
            )
        except Exception as e:
            sec_auto_ban.print("[-] WAF连接失败, Error: " + str(e))
            continue
        if r.status_code != 200:
            if r.status_code == 401:
                sec_auto_ban.print("[-] WAF登录失败")
                continue
            sec_auto_ban.print("[-] WAF连接失败")
            continue
        for i in r.json()["data"]["data"]:
            if i["event_id"] not in event_id_list and i["src_ip"] not in ip_list:
                ws_client.send_alarm(i["src_ip"], "攻击资产：" + i["host"] + " " + i["reason"])
                event_id_list.append(i["event_id"])
                if len(event_id_list) > 1000:
                    event_id_list.pop(0)
                ip_list.append(i["src_ip"])
                if len(ip_list) > 1000:
                    ip_list.pop(0)


if __name__ == "__main__":
    chaitin_waf_url = "https://xxx.xxx.xxx.xxx:9443"
    chaitin_waf_login_conf = {
        "jwt-secret": "",
        "username": "",
        "password": "",
        "bearer": "xxx.xxx.xxx"
    }
    sec_auto_ban = SecAutoBan(
        server_ip="127.0.0.1",
        server_port=8000,
        sk="sk-*****",
        client_type="alarm",
        alarm_analysis = alarm_analysis
    )
    sec_auto_ban.run()
