import jwt
import time
import datetime
import requests
from SecAutoBan import SecAutoBan
requests.packages.urllib3.disable_warnings()


def password_login() -> str:
    r = requests.get(chaitin_waf_config["url"] + "/api/open/auth/csrf", verify=False)
    if r.status_code != 200:
        return ""
    post_data = {
        "csrf_token": r.json()["data"]["csrf_token"],
        "username": chaitin_waf_config["username"],
        "password": chaitin_waf_config["password"]
    }
    r = requests.post(chaitin_waf_config["url"] + "/api/open/auth/login", json=post_data, verify=False)
    if r.status_code != 200:
        return ""
    return r.json()["data"]["jwt"]


def get_header() -> dict:
    header = {}
    if len(chaitin_waf_config["jwt-secret"]) != 0:
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
        token = jwt.encode(jwt_payload, chaitin_waf_config["jwt-secret"], algorithm='HS256')
        header["Authorization"] = "Bearer " + token
        return header
    if len(chaitin_waf_config["username"]) != 0:
        header["Authorization"] = "Bearer " + password_login()
        return header
    header["Authorization"] = "Bearer " + chaitin_waf_config["bearer"]
    return header


def alarm_analysis(ws_client):
    while True:
        time.sleep(5)
        try:
            r = requests.get(
                chaitin_waf_config["url"] + "/api/open/records?page=1&page_size=20&ip=&url=&port=&host=&attack_type=&action=1",
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
            ws_client.send_alarm(i["src_ip"], i["host"], i["reason"])


if __name__ == "__main__":
    chaitin_waf_config = {
        "url": "https://xxx.xxx.xxx.xxx:9443",
        "jwt-secret": "",
        "username": "",
        "password": "",
        "bearer": "xxx.xxx.xxx"
    }
    sec_auto_ban = SecAutoBan(
        server_ip="127.0.0.1",
        server_port=80,
        sk="sk-*****",
        client_type="alarm",
        alarm_analysis = alarm_analysis
    )
    sec_auto_ban.run()
