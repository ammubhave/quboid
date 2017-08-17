import os.path
import Queue
import signal
import subprocess
import sys
import threading
import urllib

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import Xlib.display
import Xlib.X
import xpybutil.ewmh as ewmh
from xpybutil import util

from ui_secureworkstationpanel import *

import evdev
from evdev import InputDevice, categorize, ecodes

class SetPromptWorker(QThread):
    def __init__(self, q):
        QThread.__init__(self)
        self.q = q

    def __del__(self):
        self.wait()

    def run(self):
        while True:
            message, clientsocket = self.q.get(True)
            print(message, clientsocket)
            self.emit(SIGNAL('setPrompt(QString, PyQt_PyObject)'),
                      message, clientsocket)
        self.terminate()


class SecureWorkstationPanel(Ui_SecureWorkstationPanel, QWidget):
    def __init__(self):
        super(Ui_SecureWorkstationPanel, self).__init__()
        self.setupUi(self)

        self.resize(QtGui.QDesktopWidget().screenGeometry().width(), 150)
        self.move(0, 0)
        self.setWindowFlags(self.windowFlags() |
                            QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.WindowStaysOnTopHint)
        self.prompt.hide()

        self.urlbar.returnPressed.connect(self.urlbar_navigate)
        self.closeButton.clicked.connect(self.closeButton_clicked)

        self._display = Xlib.display.Display()
        self._root = self._display.screen().root

        self.set_prompt_q = Queue.Queue()
        self.set_prompt_thread = SetPromptWorker(self.set_prompt_q)
        self.connect(self.set_prompt_thread,
                     SIGNAL('setPrompt(QString, PyQt_PyObject)'),
                     self.set_prompt)
        self.set_prompt_thread.start()

        self.urls = dict()
        self.active_vm = None

    def set_prompt(self, message, clientsocket):
        self.message.setText(message)

        def allow_clicked():
            clientsocket.send('\x01')
            clientsocket.close()
            self.prompt.hide()

        def deny_clicked():
            clientsocket.send('\x00')
            clientsocket.close()
            self.prompt.hide()
        self.allow_button.clicked.connect(allow_clicked)
        self.deny_button.clicked.connect(deny_clicked)
        self.urlbar.setFocusPolicy(Qt.StrongFocus)
        self.prompt.show()

    def active_window_change_listen(self):
        self._root.change_attributes(event_mask=Xlib.X.PropertyChangeMask)

        def _f():
            NET_ACTIVE_WINDOW = self._display.intern_atom(
                '_NET_ACTIVE_WINDOW')
            while True:
                event = self._display.next_event()
                if (event.type == Xlib.X.PropertyNotify and
                        event.atom == NET_ACTIVE_WINDOW):
                    window_id = \
                        self._root.get_full_property(
                            NET_ACTIVE_WINDOW,
                            Xlib.X.AnyPropertyType).value[0]
                    try:
                        vmname = util.PropertyCookie(util.get_property(window_id, '_QUBES_VMNAME')).reply()
                        if vmname is not None and vmname.startswith('disp'):
                            url = self.urls.get(vmname[4:], '<Loading...>')
                            self.urlbar.setText(url)
                            self.active_vm = vmname
                            self.urls[vmname[4:]] = subprocess.check_output("qvm-run sys-firewall --pass-io 'echo %s | /home/user/quboid/sys-firewall/mitmproxy/get_origin.py'" % vmname, shell=True)
                            self.urlbar.setText(self.urls[vmname[4:]])
                        else:
                            self.urlbar.setText('')
                    except Exception as ex:
                        pass
        thread = threading.Thread(target=_f)
        thread.start()

    def urlbar_navigate(self):
        url = str(self.urlbar.text())
        next_dispid = '1'
        if os.path.exists('/var/run/qubes/dispid'):
            with open('/var/run/qubes/dispid') as f:
                next_dispid = f.read()
        self.urls[next_dispid] = url

        def _navigate(url):
            subprocess.call("echo 'firefox %s' | "
                            "/usr/lib/qubes/qfile-daemon-dvm "
                            "qubes.VMShell dom0 DEFAULT "
                            "red" % (urllib.quote(url.encode('utf8'))),
                            shell=True)
        thread = threading.Thread(target=_navigate, args=[url])
        thread.start()

    def closeButton_clicked(self):
        if self.active_vm is None:
            sys.exit(0)
        else:
            subprocess.call("/usr/bin/qvm-remove " + self.active_vm, shell=True)
            self.active_vm = None

    def secure_workstation_netfilter_daemon_listen(self):
        def _f():
            import socket
            HOST = 'localhost'
            PORT = 10294
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen(1)
            while 1:
                (clientsocket, address) = s.accept()
                r = ''
                while True:
                    b = clientsocket.recv(1)
                    if b == '\x00':
                        break
                    r += b

                src_vm, dst = r.strip().split()

                print(src_vm, self.urls[src_vm[5:-1]], dst)
                if src_vm.startswith('<disp') and self.urls[src_vm[5:-1]] == dst:
                    clientsocket.send('\x01')
                    clientsocket.close()
                else:
                    self.set_prompt_q.put(('Connection attempt to ' + dst +
                                           ' from ' + src_vm,
                                           clientsocket))

                print(src_vm, r)
        thread = threading.Thread(target=_f)
        thread.start()


def main():
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    global app
    app = QApplication(sys.argv)

    global panel
    panel = SecureWorkstationPanel()
    panel.show()
    panel.active_window_change_listen()
#    panel.secure_workstation_netfilter_daemon_listen()

    app.exec_()


if __name__ == "__main__":
    main()
