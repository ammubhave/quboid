#!/bin/sh

sudo dnf install libffi-devel openssl-devel gcc gcc-c++ redhat-rpm-config
mkdir -p "$HOME/quboid-mitmproxy"
cp "`dirname $0`/mitmproxy/intercept.py" "$HOME/quboid-mitmproxy"
python35 -m venv "$HOME/quboid-mitmproxy/venv"
source "$HOME/quboid-mitmproxy/venv/bin/activate"
pip install mitmproxy
deactivate

mkdir -p "$HOME/.config/systemd/user"
cp "`dirname $0`/mitmproxy/mitmproxy.service" "$HOME/.config/systemd/user"
