import time
import requests
import math
from SecAutoBan import SecAutoBan
requests.packages.urllib3.disable_warnings()


def alarm_analysis(ws_client):
    while True:
        time.sleep(30) # 每隔30秒获取一次蜜罐数据,可根据实际情况调整
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
        post_data_total = {
            "start_time": 0,
            "end_time": 0,
            "page_no": 1,
            "page_size": 1,
            "intranet": 0,
            "threat_label": [],
            "client_id": [],
            "service_name": [],
            "info_confirm": "0"
        }
        try:
            url = hfish_config["url"] + "/api/v1/attack/detail?api_key=" + hfish_config["api_key"]
            r_total = requests.post(url, json=post_data_total, verify=False) # 获取蜜罐数据总量
            if r_total.status_code != 200 or r_total.json()["verbose_msg"] != "成功":
                sec_auto_ban.print("[-] 获取蜜罐数据失败")
                continue
            data = r_total.json()
            total_num = data["data"]["total_num"]
            page_size = post_data["page_size"]
            total_pages = math.ceil(total_num / page_size)  # 向上取整
            post_data["page_no"] = total_pages # 设置page_no为最后一页
            r = requests.post(url, json=post_data, verify=False)
        except Exception as e:
            sec_auto_ban.print("[-] 获取蜜罐数据失败, Error: " + str(e))
            continue
        if r.status_code != 200:
            sec_auto_ban.print("[-] 获取蜜罐数据失败")
            continue
        if r.json()["verbose_msg"] != "成功":
            sec_auto_ban.print("[-] 获取蜜罐数据失败")
            continue
        for i in r.json()["data"]["detail_list"]:
            ws_client.send_alarm(i["attack_ip"], "蜜罐", i["service_name"])


if __name__ == "__main__":
    hfish_config = {
        "url": "https://xxx.xxx.xxx.xxx:4433",
        "api_key": "xxx"
    }
    sec_auto_ban = SecAutoBan(
        server_ip="127.0.0.1",
        server_port=80,
        sk="sk-*****",
        client_type="alarm",
        alarm_analysis = alarm_analysis
    )
    sec_auto_ban.run()
