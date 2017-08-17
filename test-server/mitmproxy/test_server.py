import mitmproxy
import re
from mitmproxy.script import concurrent

reddit_patterns = [r'https?:\/\/.*reddit\.com.*',
                   r'https?:\/\/.*\.redditmedia\.com\/.*',
                   r'https?:\/\/www\.redditstatic\.com\/.*']

@concurrent
def request(flow):
    pass

@concurrent
def response(flow):
    url = flow.request.pretty_url
    print(flow.response.headers, flow.request.pretty_url)
    for pattern in reddit_patterns:
        if re.match(pattern, url):
            flow.response.headers["Origin"] = 'reddit.com'
            flow.response.headers.set_all("Origin-Pattern", [r'https?:\/\/.*reddit\.com.*',
               r'https?:\/\/.*\.redditmedia\.com\/.*',
               r'https?:\/\/www\.redditstatic\.com\/.*'])
            print("matched")
            return

