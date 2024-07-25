import json
import socketserver
from SecAutoBan import SecAutoBan


class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server, ws_client):
        self.ws_client = ws_client
        super().__init__(request, client_address, server)
    def handle(self):
        data = self.request[0]
        message = data.decode('utf-8')
        messages = message.split('\n')
        for msg in messages:
            if msg == "":
                continue
            msg = json.loads(msg.split(" - - - - ")[1])
            if "attackIp" not in msg:
                continue
            if msg["attackIp"] == "":
                continue
            if bypass_lan and msg["attackIpAddress"] == "局域网":
                continue
            self.ws_client.send_alarm(msg["attackIp"], msg["action"]["text"])


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
