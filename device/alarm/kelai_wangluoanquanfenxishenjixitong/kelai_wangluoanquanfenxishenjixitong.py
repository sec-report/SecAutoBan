import json
import ipaddress
import socketserver
from SecAutoBan import SecAutoBan


def is_lan(ip: str) -> bool:
    if bypass_lan:
        return ipaddress.ip_address(ip).is_private
    return False


class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server, ws_client):
        self.ws_client = ws_client
        super().__init__(request, client_address, server)
    def handle(self):
        data = self.request[0]
        if len(data) == 0:
            return
        message = data.decode('utf-8')
        msg = json.loads(message.split(" localhost.localdomain ")[1])
        if "websec_attack_ip" not in msg:
            return
        sip = msg["websec_attack_ip"]
        if sip == "":
            return
        if is_lan(sip):
            return
        origin = "攻击" + msg["websec_victim_ip"] + ": " + msg["alarm_name"]
        self.ws_client.send_alarm(sip, origin)



def alarm_analysis(ws_client):
    with socketserver.ThreadingUDPServer(("0.0.0.0", listen_syslog_udp_port), lambda *args: SyslogUDPHandler(*args, ws_client=ws_client)) as server:
        sec_auto_ban.print("[+] 监听SysLog端口: " + str(listen_syslog_udp_port) + "/UDP")
        server.serve_forever()


if __name__ == "__main__":
    listen_syslog_udp_port = 567
    bypass_lan = True  # 过滤内网攻击，True 开启 | False 关闭
    sec_auto_ban = SecAutoBan(
        server_ip="127.0.0.1",
        server_port=80,
        sk="sk-*****",
        client_type="alarm",
        alarm_analysis = alarm_analysis
    )
    sec_auto_ban.run()
