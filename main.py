#!/usr/bin/env python3
import socket, paho.mqtt.client, time, threading, logging, os

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO").upper())
log = logging.getLogger("ipv6canvas")

class Canvas:
    def __init__(self, width, height, mqttc):
        if not width or not height:
            raise ValueError("Width and height must be greater than 0")

        self._width = width
        self._height = height
        self._mqttc = mqttc

        self.rows = [bytearray(b"\xff" * 3 * width) for _ in range(height)]

        self._publishLock = threading.Lock()
        self._pendingRows = set()
        self._publishing = False


    def loadFromMQTT(self):
        loadedRows = 0

        def loadLine(mqttc, userdata, m):
            nonlocal loadedRows

            if not m.retain:
                # Only load from old messages
                return

            try:
                self.rows[int(m.topic)] = bytearray(m.payload)
            except Exception:
                log.error('Exception while loading topic "%s":', m.topic, exc_info=True)

            loadedRows += 1
            if loadedRows >= self._height:
                log.info("MQTT state load complete")
                mqttc.unsubscribe("#")
                mqttc.message_callback_remove("#")

        log.info("Starting state load from MQTT")
        self._mqttc.message_callback_add("#", loadLine)
        self._mqttc.subscribe("#")


    def _publisher(self):
        # Only publish 1 row every 0.01s to reduce load
        try:
            self._publishing = True

            while True:
                time.sleep(0.02)

                if self._pendingRows:
                    with self._publishLock:
                        y = self._pendingRows.pop()
                        self._mqttc.publish(str(y), self.rows[y], retain=True)
        finally:
            self._publishing = False


    def startPublishing(self):
        if not self._publishing:
            log.info("Starting publish thread")
            threading.Thread(target=self._publisher, daemon=True).start()


    def setPixel(self, x, y, r, g, b):
        if x >= self._width or y >= self._height:
            raise ValueError(f"Coordinates {(x, y)} are out of bounds")

        if any(c > 255 for c in (r, g, b)):
            raise ValueError(f"Colour {(r, g, b)} is out of range")

        offset = x * 3
        colour = bytearray((r, g, b))

        if self.rows[y][offset:offset+3] != colour:
            with self._publishLock:
                self.rows[y][offset:offset+3] = colour

                self._pendingRows.add(y)



class RateLimiter():
    def __init__(self):
        self._lastReset = time.time()
        self._buckets = {}
        self._reaping = False


    def _reaper(self):
        try:
            self._reaping = True

            while True:
                time.sleep(10)
                self._buckets = {}
        finally:
            self._reaping = False


    def startReaping(self):
        if not self._reaping:
            log.info("Starting RateLimiter reaping")
            threading.Thread(target=self._reaper, daemon=True).start()


    def count(self, addr):
        addr = socket.inet_pton(socket.AF_INET6, addr)[:6]

        try:
            self._buckets[addr] += 1
        except KeyError:
            self._buckets[addr] = 1

        return self._buckets[addr] < 128*128



mqttc = paho.mqtt.client.Client()
mqttc.connect("::1")
mqttc.loop_start()

canvas = Canvas(256, 256, mqttc)
canvas.loadFromMQTT()
canvas.startPublishing()

ratelim = RateLimiter()
ratelim.startReaping()

canvasPrefix = socket.inet_pton(socket.AF_INET6, "2400:8902:e001:233::")[:8]

sock = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_ICMPV6)
sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_RECVPKTINFO, 1)

log.info("Starting main loop")
while True:
    data = sock.recvmsg(1, 32)
    if data[0] == b"\x80":
        # ICMPv6 echo request
        pingDst = data[1][0][2][:16]

        if pingDst[:8] == canvasPrefix and ratelim.count(data[3][0]):
            # 2400:8902:e001:233:XXYY:RR:GG:BB
            x = pingDst[8]
            y = pingDst[9]
            r = pingDst[11]
            g = pingDst[13]
            b = pingDst[15]

            try:
                canvas.setPixel(x, y, r, g, b)
            except ValueError as e:
                log.error("ValueError while setting pixel: %s", e)
