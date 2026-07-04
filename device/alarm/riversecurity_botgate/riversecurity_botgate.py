import os
import json
import time
import socketserver
from collections import defaultdict
from threading import Lock
from SecAutoBan import SecAutoBan


# 瑞数动态安全的告警取舍：
# 正常浏览器首次访问无动态token会被412并下发JS，算出token后续请求即200，
# 所以偶发的412不是攻击。真正的爬虫/自动化工具不会执行JS，永远算不出token，
# 会在窗口内持续412。因此这里用「强特征即时告警 + 弱特征滑动窗口计数」两条路：
#   1. 命中瑞数明确的爬虫特征(ua_bot / extra_detect_matched) -> 直接告警
#   2. 其余412在 window_seconds 内累计达到 count_threshold 次 -> 告警
# 命中「爬虫却宣称是浏览器」这类矛盾特征时视为强特征。


# 强特征：命中即认为是恶意自动化，直接告警
STRONG_EXTRA_DETECT = {
    "ChromeNoAcceptLanguage",  # 声称Chrome却无Accept-Language
}


class SlidingWindowCounter:
    def __init__(self, window_seconds, threshold):
        self.window_seconds = window_seconds
        self.threshold = threshold
        self.records = defaultdict(list)
        self.alarmed = {}  # ip -> 上次告警时间，避免重复刷告警
        self.lock = Lock()

    def hit(self, ip):
        now = time.time()
        with self.lock:
            timestamps = self.records[ip]
            timestamps.append(now)
            # 清理窗口外的记录
            cutoff = now - self.window_seconds
            while timestamps and timestamps[0] < cutoff:
                timestamps.pop(0)
            if len(timestamps) < self.threshold:
                return False
            # 达到阈值，判断是否在冷却期内(默认按窗口冷却，避免同一IP高频重复告警)
            last = self.alarmed.get(ip, 0)
            if now - last < self.window_seconds:
                return False
            self.alarmed[ip] = now
            return True


class SyslogUDPHandler(socketserver.DatagramRequestHandler):
    def __init__(self, request, client_address, server, ws_client):
        self.ws_client = ws_client
        super().__init__(request, client_address, server)

    def handle(self):
        data = self.request[0]
        if len(data) == 0:
            return
        for line in data.decode('utf-8', errors='ignore').split('\n'):
            index = line.find('{')
            if index == -1:
                continue
            try:
                msg = json.loads(line[index:])
            except json.JSONDecodeError:
                continue
            self.process(msg)

    def process(self, msg):
        attack_type = msg.get("attack_type")
        if not attack_type:
            return
        src_ip = msg.get("real_remote_addr") or msg.get("src_ip", "")
        if src_ip == "":
            return
        dst_ip = msg.get("dst_ip", "")
        anomaly = msg.get("anomaly_subcategory") or msg.get("anomaly_category") or []
        location = msg.get("http_host", "") + msg.get("path", "")

        # 1. 强特征：瑞数明确判定为爬虫，或命中矛盾特征，直接告警
        strong_reason = self.match_strong(msg)
        if strong_reason:
            alarm_info = "[%s]%s %s (%s)" % (
                ",".join(attack_type), ",".join(anomaly), location, strong_reason)
            self.ws_client.send_alarm(src_ip, dst_ip, alarm_info)
            return

        # 2. 弱特征：仅当同一IP在窗口内持续412达到阈值才告警(过滤正常首访)
        if counter.hit(src_ip):
            alarm_info = "[%s]%s %s (窗口内412达到%d次)" % (
                ",".join(attack_type), ",".join(anomaly), location, count_threshold)
            self.ws_client.send_alarm(src_ip, dst_ip, alarm_info)

    @staticmethod
    def match_strong(msg):
        if msg.get("ua_bot") is True:
            return "ua_bot"
        matched = set(msg.get("extra_detect_matched") or [])
        hit = matched & STRONG_EXTRA_DETECT
        if hit:
            return ",".join(sorted(hit))
        return ""


def alarm_analysis(ws_client):
    with socketserver.ThreadingUDPServer(("0.0.0.0", listen_syslog_udp_port), lambda *args: SyslogUDPHandler(*args, ws_client=ws_client)) as server:
        sec_auto_ban.print("[+] 监听SysLog端口: " + str(listen_syslog_udp_port) + "/UDP")
        sec_auto_ban.print("[+] 弱特征阈值: %d秒内412达到%d次告警" % (window_seconds, count_threshold))
        server.serve_forever()


if __name__ == "__main__":
    listen_syslog_udp_port = int(os.getenv("listen_port", 514))
    window_seconds = int(os.getenv("window_seconds", 30))
    count_threshold = int(os.getenv("count_threshold", 20))
    counter = SlidingWindowCounter(window_seconds, count_threshold)
    sec_auto_ban = SecAutoBan(
        server_ip=os.getenv("server_ip", "127.0.0.1"),
        server_port=int(os.getenv("server_port", 80)),
        sk=os.getenv("sk"),
        client_type="alarm",
        alarm_analysis = alarm_analysis
    )
    sec_auto_ban.run()
