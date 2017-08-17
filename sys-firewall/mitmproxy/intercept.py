# import libmproxy
import mitmproxy
import subprocess
import threading

from collections import defaultdict
from mitmproxy import ctx
from mitmproxy.script import concurrent
import tld
import re
import base64
import json
import urllib.request
import socket
import os


def get_vmname_from_ip(ip):
    return subprocess.getoutput('echo %s | /bin/qrexec-client-vm dom0 '
                                'qubes.QuboidGetVmnameFromIp' % ip)


# def get_url_from_vmname(vmname):
#     return "reddit.com"
#     return subprocess.getoutput('echo %s | /bin/qrexec-client-vm dom0 '
#                                 'qubes.QuboidGetUrlFromVmname' % vmname)


# def set_url_for_vmname(vmname, vmurl):
#     pass


class SecureWorkstationProxy2:
    def __init__(self):
        # vmname(str) -> list[pattern(str)]
        self.same_origin_patterns = {}

        # vmname(str) -> list[pattern(str)]
        self.allowed_external_patterns = {}

        # vmname(str) -> origin(name)
        self.origins = {}

        self.get_origin_listener_thread = threading.Thread(target=self._get_origin_listener)
        self.get_origin_listener_thread.start()

    def _get_origin_listener(self):
        if os.path.exists('/tmp/quboid_get_origin.sock'):
            os.remove('/tmp/quboid_get_origin.sock')
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind('/tmp/quboid_get_origin.sock')
        server.listen(1)
        while True:
            connection, client_address = server.accept()
            try:
                vmname = ''
                while True:
                    c = connection.recv(1).decode('utf-8')
                    if c:
                        if c == '\n':
                            break
                        vmname += str(c)
                    else:
                        break
                vmname = '<' + vmname + '>'
                if vmname in self.origins:
                    connection.send(self.origins[vmname].encode('utf-8'))
                else:
                    connection.send("<unknown>".encode('utf-8'))
            finally:
                connection.close()

    def _is_same_origin(self, vmname, url):
        for pattern in self.same_origin_patterns[vmname]:
            if re.match(pattern, url):
                return True
        return False

    def _is_url_approved(self, vmname, url):
        for pattern in self.allowed_external_patterns[vmname]:
            if re.match(pattern, url):
                return True
        return False

    def request(self, flow):
        try:
            print(flow.request.pretty_url)
            vmname = get_vmname_from_ip(flow.client_conn.address.host)
            print(vmname, self.origins)

            if vmname not in self.origins:
                try:
                    # This is the first request in this VM, associate origin
                    request = urllib.request.Request(flow.request.pretty_url)
                    response = urllib.request.urlopen(request)
                    origin = response.getheader('Origin')

                    if origin is None:
                        raise Exception('No origin specified')

                    self.origins[vmname] = origin
                    if not origin.startswith('http'):
                        origin = 'http://' + origin
                    request = urllib.request.Request(origin)
                    response = urllib.request.urlopen(request)
                    same_origin_patterns = response.getheader('Origin-Pattern')
                    allowed_external_patterns = response.getheader('Allowed-External-Pattern')
                    if same_origin_patterns is not None:
                        self.same_origin_patterns[vmname] = list(map(str.strip, same_origin_patterns.split(',')))
                    else:
                        self.same_origin_patterns[vmname] = []
                    if allowed_external_patterns is not None:
                        self.allowed_external_patterns[vmname] = list(map(str.strip, allowed_external_patterns.split(',')))
                    else:
                        self.allowed_external_patterns[vmname] = []
                except Exception as ex:
                    if vmname in self.origins:
                        del self.origins[vmname]
                    raise ex

            print(self.same_origin_patterns, self.origins)

            if self._is_same_origin(vmname, flow.request.pretty_url):
                return

            if self._is_url_approved(vmname, flow.request.pretty_url) and \
                    'Referer' in flow.request.headers and \
                        (self._is_same_origin(vmname, flow.request.headers['Referer']) or \
                         self._is_url_approved(vmname, flow.request.headers['Referer'])):
                return

            # p = subprocess.getoutput('echo ' + flow.client_conn.address.host +
            #                          ' ' + flow.request.host_header +
            #                          '| /bin/qrexec-client-vm dom0 '
            #                          'qubes.SecureWorkstationNetfilter')
            # approved = (p.strip() == "1")
            # if approved:
            #     return
        except Exception as ex:
            print('Exception', ex)
            pass
        flow.response = mitmproxy.http.HTTPResponse.make(403)

    def response(self, flow):
        if flow.response.status_code == 403:
            return
        vmname = get_vmname_from_ip(flow.client_conn.address.host)

        if not self._is_same_origin(vmname, flow.request.pretty_url):
            return

        if 'Origin-Pattern' in flow.response.headers:
            same_origin_patterns = flow.response.headers['Origin-Pattern'].split(',')
            for pattern in same_origin_patterns:
                if pattern not in self.same_origin_patterns[vmname]:
                    self.same_origin_patterns[vmname].append(pattern)

        if 'Allowed-External-Pattern' in flow.response.headers:
            allowed_external_patterns = flow.response.headers['Allowed-External-Pattern'].split(',')
            for pattern in allowed_external_patterns:
                if pattern not in self.allowed_external_patterns[vmname]:
                    self.allowed_external_patterns[vmname].append(pattern)

def start():
    return SecureWorkstationProxy2()

# prelist = {
#     'sb.scorecardresearch.com': '0',
#     'www.google-analytics.com': '0',
#     '*.doubleclick.net': '0',
#     'ajax.googleapis.com': '1',
#     '*.bootstrapcdn.com': '1',
# }


# class SecureWorkstationProxy:
#     def __init__(self):
#         self.rules = defaultdict(dict)
#         self.rules_lock = thread.Lock()

#     def _is_host_approved(address, host):
#         while True:
#             if host in prelist:
#                 return prelist[host] == '1'
#             if host in rules[address]:
#                 return rules[address][host] == '1'
#             try:
#                 host = host[host.index('.') + 1:]
#                 if ('*.' + host) in prelist:
#                     return prelist['*.' + host] == '1'
#                 if ('*.' + host) in rules[address]:
#                     return rules[address]['*.' + host] == '1'
#             except ValueError:
#                 return None

#     def is_host_approved(address, host):
#         self.rules_lock.acquire()
#         ret = _is_host_approved(address, host)
#         self.rules_lock.release()
#         return ret

#     @concurrent
#     def request(flow):
#         # Check if 
#         try:
#             tld.get_tld(flow.request.host_header, fix_protocol=True)
#         except tld.exceptions.TldDomainNotFound as e:
#             flow.kill()
#             return

#         approved = _is_host_approved(flow.client_conn.address.host,
#                                      flow.request.host_header)
#         if approved is None:
#             request_prompt(flow)
#             approved = _is_host_approved(flow.client_conn.address.host, flow.request.host_header)
#             if approved is None:
#                 rules[flow.client_conn.address.host][flow.request.host_header] = '0'
#                 p = subprocess.getoutput('echo ' + flow.client_conn.address.host +
#                                          ' ' + flow.request.host_header +
#                                          '| /bin/qrexec-client-vm dom0 '
#                                          'qubes.SecureWorkstationNetfilter')
#                 rules[flow.client_conn.address.host][flow.request.host_header] = \
#                     p.strip()
#                 approved = \
#                     rules[flow.client_conn.address.host][flow.request.host_header] == \
#                     '1'

#         if not approved:
#             flow.response = mitmproxy.http.HTTPResponse.make(403)


# def request_prompt(flow):



# def responseheaders(flow):
#     global r
#     if flow.server_conn.ssl_established:
#         ctx.log.error(flow.request.host_header + ' ' + str('alts:' + str(flow.server_conn.cert.altnames)))
#         for name in flow.server_conn.cert.altnames:
#             name = str(name, 'utf-8')
#             rules[flow.client_conn.address.host][name] = '1'
#     if r == flow.request.url:
#         r = None
#         rlock.release()
#         # print(flow.server_conn.cert.altnames, flow.server_conn.cert.cn)

#     # print(flow.client_conn.address.host)
#     # print(flow.request.host, flow.request.host_header)

# def error(flow):
#     global r
#     if r == flow.request.url:
#         r = None
#         rlock.release()
#     return
