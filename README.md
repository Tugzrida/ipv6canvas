# ipv6canvas

This repo contains all the source and conf required to make the [IPv6 Canvas](https://blog.tugzrida.xyz/2023/02/06/introducing-the-ipv6-canvas/). It's not at all organised or optimised, so peruse at your own risk!

## Files
- `certbot/`: Conf files to handle obtaining and deploying TLS cert
- `mosquitto/`: Mosquitto MQTT broker conf files for conveying updates to clients
- `writers/`: Some of my own scripts I hacked together in the rush to draw on the canvas
- `index.html`: Client front-end
- `ipv6canvas.service`: systemd service file to run `main.py`
- `main.py`: Python script to receive pings and update the canvas
- `nginx_site`: nginx conf
- `systemd-network-range.conf`: systemd local route conf for the IPv6 prefix, should be placed somewhere under `/etc/systemd/network/`

🏳️‍⚧️ 🏳️‍🌈  
🏳️‍⚧️ 🏳️‍🌈
