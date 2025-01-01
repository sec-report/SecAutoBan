import socketserver
from SecAutoBan import SecAutoBan

# 假设Syslog格式为`攻击IP\t被攻击资产\t报警详情，例如：1.1.1.1\t127.0.0.1\tNMAP 扫描`
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
            self.ws_client.send_alarm(msg.split('\t')[0], msg.split('\t')[1], msg.split('\t')[2])


def alarm_analysis(ws_client):
    with socketserver.ThreadingUDPServer(("0.0.0.0", listen_syslog_udp_port), lambda *args: SyslogUDPHandler(*args, ws_client=ws_client)) as server:
        print("[+] 监听SysLog端口: " + str(listen_syslog_udp_port) + "/UDP")
        server.serve_forever()


if __name__ == "__main__":
    listen_syslog_udp_port = 567
    sec_auto_ban = SecAutoBan(
        server_ip="127.0.0.1",
        server_port=80,
        sk="sk-*****",
        client_type="alarm",
        alarm_analysis = alarm_analysis
    )
    sec_auto_ban.run()
