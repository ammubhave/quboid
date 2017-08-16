# quboid
Quboid: A Secure Workstation for Web Interaction

Prerequisites:
- Python 3.5 or higher



# Testing

## How to setup test server

- Create a new Qubes VM (ProxyVM). Set its NetVM to sys-net.
- sudo dnf install libffi-devel redhat-rpm-config gcc gcc-c++ openssl-devel redhat-rpm-config
- cd test_server
- python35 -m venv venv
- source venv/bin/activate
- pip install mitmproxy

