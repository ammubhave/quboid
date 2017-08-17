#!/usr/bin/env python

import socket
import sys

s = socket.socket(socket.AF_UNIX)
s.settimeout(5)
s.connect('/tmp/quboid_get_origin.sock')
s.send(sys.stdin.read().strip() + '\n')
print(s.recv(256))
s.close()
