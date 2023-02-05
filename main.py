#!/usr/bin/env python3
import socket, ipaddress, paho.mqtt.client

canvasSubnet = ipaddress.IPv6Network("2400:8902:e001:233::/64")

sock = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_ICMPV6)
sock.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_RECVPKTINFO, 1)

mqtt = paho.mqtt.client.Client()
mqtt.connect("::1")
mqtt.loop_start()


def setPixel(x, y, r, g, b):
    mqtt.publish(f"{y}/{x}", f"{r:02x}{g:02x}{b:02x}", retain=True)


while True:
    data = sock.recvmsg(1, 32)
    if data[0] == b"\x80":
        # ICMPv6 echo request
        pingDstRaw = data[1][0][2][:16]
        pingDst = ipaddress.IPv6Address(pingDstRaw)

        if pingDst in canvasSubnet:
            x = pingDstRaw[8]
            y = pingDstRaw[9]
            r = pingDstRaw[11]
            g = pingDstRaw[13]
            b = pingDstRaw[15]

            setPixel(x, y, r, g, b)
