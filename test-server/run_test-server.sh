#!/bin/sh
source mitmproxy/venv/bin/activate
mitmdump -T -s mitmproxy/test_server.py
deactivate
