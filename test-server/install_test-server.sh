#!/bin/sh

sudo iptables -t nat -I PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
sudo iptables -t nat -I PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 8080
sudo iptables -I INPUT -p tcp --dport 8080 -j ACCEPT

sudo dnf -y install gcc gcc-c++ libffi-devel openssl-devel redhat-rpm-config

python35 -m venv mitmproxy/venv
source mitmproxy/venv/bin/activate
pip install mitmproxy
deactivate
