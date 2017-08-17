#!/usr/bin/env python3
import sys, shlex, subprocess
s = sys.stdin.read().strip()
print(s)
print(shlex.quote(s))
subprocess.call("echo 'firefox %s' | /usr/lib/qubes/qfile-daemon-dvm qubes.VMShell dom0 DEFAULT red" % shlex.quote(s), shell=True)
