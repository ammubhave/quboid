#!/usr/bin/env python2
import sys
import subprocess

srcip = sys.stdin.read().strip()
vmname = "<none>"
for line in subprocess.check_output(['/usr/bin/qvm-ls',
                                     '--raw-data', 'name', 'ip']).splitlines():
    name, ip = line.split('|')
    if ip == srcip:
        vmname = name
        break
print(vmname)
