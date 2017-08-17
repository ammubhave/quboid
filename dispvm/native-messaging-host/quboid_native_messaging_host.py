#!/usr/bin/env python3

import sys, json, struct, shlex, subprocess

rawLength = sys.stdin.read(4).encode('utf-8')
if len(rawLength) == 0:
    print("ERROR")
    sys.exit(0)
messageLength = struct.unpack('@I', rawLength)[0]
message = json.loads(sys.stdin.read(messageLength))
subprocess.call("echo " + shlex.quote(message) + " | /bin/qrexec-client-vm dom0 qubes.QuboidOpenUrl", shell=True)
print("OK")
