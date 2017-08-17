import mitmproxy
import re
from mitmproxy.script import concurrent

#reddit_patterns = [r'https?:\/\/.*reddit\.com.*',
#                   r'https?:\/\/.*\.redditmedia\.com\/.*',
#                   r'https?:\/\/www\.redditstatic\.com\/.*']
#mitfcu_patterns = [r'https?:\/\/.*mitfcu\.org.*',
#                   r'https?:\/\/.*mitfcu2\.org.*']

patterns = [
    ([r'https?:\/\/.*reddit\.com.*',
      r'https?:\/\/.*\.redditmedia\.com\/.*',
      r'https?:\/\/www\.redditstatic\.com\/.*'], 'reddit.com'),
    ([r'https?:\/\/.*mitfcu\.org.*',
      r'https?:\/\/.*mitfcu2\.org.*'], 'mitfcu.org'),
    ([r'https?:\/\/.*yelp\.com.*',
      r'https?:\/\/.*yelpcdn\.com.*'], 'yelp.com'),
    ([r'https?:\/\/.*google\.com.*',
      r'https?:\/\/.*googleusercontent\.com.*',
      r'https?:\/\/.*gstatic\.com.*',
      r'https?:\/\/.*googleapis\.com.*'], 'google.com'),
    ([r'https?:\/\/.*speedtest\.net.*',
      r'https?:\/\/.*beld\.net.*',
      r'https?:\/\/.*cdnst\.net.*'], 'speedtest.net'),
]

@concurrent
def request(flow):
    pass

@concurrent
def response(flow):
    url = flow.request.pretty_url
    print(flow.response.headers, flow.request.pretty_url)
    for ps, origin in patterns:
        for pattern in ps:
            if re.match(pattern, url):
                flow.response.headers["Origin"] = origin
                flow.response.headers.set_all("Origin-Pattern", ps)
                return

