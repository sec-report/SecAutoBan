import socketserver
from SecAutoBan import SecAutoBan


class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def __init__(self, request, client_address, server, ws_client):
        self.ws_client = ws_client
        super().__init__(request, client_address, server)
    def handle(self):
        data = self.request[0]
        message = data.decode('utf-8')
        if "  action:Block  " not in message:
            return
        src_ip = ""
        dst_ip = ""
        event_type = ""
        for i in message.split("  "):
            if i[:7] == "src_ip:":
                src_ip = i[7:]
                continue
            if i[:7] == "dst_ip:":
                dst_ip = i[7:]
                continue
            if i[:11] == "event_type:":
                if i[11:] == "Info_Leak":
                    return
                if i[11:] == "WEB Access Logs":
                    return
                event_type = i[11:]
            if src_ip != "" and dst_ip != "" and event_type != "":
                break
        self.ws_client.send_alarm(src_ip, dst_ip, event_type)


def alarm_analysis(ws_client):
    with socketserver.ThreadingUDPServer(("0.0.0.0", listen_syslog_udp_port), lambda *args: SyslogUDPHandler(*args, ws_client=ws_client)) as server:
        sec_auto_ban.print("[+] 监听SysLog端口: " + str(listen_syslog_udp_port) + "/UDP")
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
