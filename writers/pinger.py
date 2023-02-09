#!/usr/bin/env python3
import socket, time

sock = socket.socket(socket.AF_INET6, socket.SOCK_RAW, socket.IPPROTO_ICMPV6)

def sendPing(x, y, colour):
    addr = f"2400:8902:e001:233:{x:02x}{y:02x}:{colour[0]:02x}:{colour[1]:02x}:{colour[2]:02x}"
    sock.sendto(b"\x80\0\0\0\0\0\0\0", (addr, 0))





red    = (0xcf, 0x0f, 0x0f)
orange = (0xff, 0xa0, 0x00)
yellow = (0xff, 0xd2, 0x00)
green  = (0x36, 0xa0, 0x30)
blue   = (0x1b, 0x77, 0xcd)
purple = (0x4d, 0x14, 0x8c)

pink   = (0xf5, 0xa7, 0xb8)
white  = (0xff, 0xff, 0xff)
lblu   = (0x5b, 0xce, 0xfa)

rainbow_colours = [red, orange, yellow, green, blue, purple]
trans_colours = [lblu, pink, white, pink, lblu]


for i, colour in enumerate(trans_colours):
    y = 226 + (i*6)
    for x in range(128, 192):

        sendPing(x, y, colour)
        sendPing(x, y+1, colour)
        sendPing(x, y+2, colour)
        sendPing(x, y+3, colour)
        sendPing(x, y+4, colour)
        sendPing(x, y+5, colour)

for i, colour in enumerate(rainbow_colours):
    y = 226 + (i*5)
    for x in range(192, 256):

        sendPing(x, y, colour)
        sendPing(x, y+1, colour)
        sendPing(x, y+2, colour)
        sendPing(x, y+3, colour)
        sendPing(x, y+4, colour)
