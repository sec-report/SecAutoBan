import time
import requests
from SecAutoBan import SecAutoBan
requests.packages.urllib3.disable_warnings()


def alarm_analysis(ws_client):
    ip_list = []
    while True:
        time.sleep(5)
        post_data = {
            "start_time": 0,
            "end_time": 0,
            "page_no": 1,
            "page_size": 20,
            "intranet": 0,
            "threat_label": [],
            "client_id": [],
            "service_name": [],
            "info_confirm": "0"
        }
        try:
            r = requests.post(hfish_url + "/api/v1/attack/detail?api_key=" + hfish_api_key, json=post_data, verify=False)
        except Exception as e:
            sec_auto_ban.print("[-] 获取蜜罐数据失败")
            print("[-] Error: " + str(e))
            continue
        if r.status_code != 200:
            sec_auto_ban.print("[-] 获取蜜罐数据失败")
            continue
        if r.json()["verbose_msg"] != "成功":
            sec_auto_ban.print("[-] 获取蜜罐数据失败")
            continue
        for i in r.json()["data"]["detail_list"]:
            if i["attack_ip"] not in ip_list:
                ws_client.send_alarm(i["attack_ip"], "攻击" + i["service_name"])
                ip_list.append(i["attack_ip"])
                if len(ip_list) > 10000:
                    ip_list.pop(0)


if __name__ == "__main__":
    hfish_url = "https://xxx.xxx.xxx.xxx:4433"
    hfish_api_key = "xxx"
    sec_auto_ban = SecAutoBan(
        server_ip="127.0.0.1",
        server_port=8000,
        sk="sk-*****",
        client_type="alarm",
        alarm_analysis = alarm_analysis
    )
    sec_auto_ban.run()
