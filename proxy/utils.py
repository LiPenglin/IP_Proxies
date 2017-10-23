import requests

from requests.exceptions import ConnectionError

base_headers = {
    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.110 Safari/537.36",
    "Accept-Encoding" : "gzip, deflate, sdch",
    "Accept-Language" : "zh-CN,zh;q=0.8,en;q=0.6"
}

def get_page(url, option = {}):
    headers = dict(base_headers, **option)
    print("Getting", url)
    try:
        r = requests.get(url, headers)
        print("Getting result", url, r.status_code)
        if r.status_code == 200:
            return r.text
    except ConnectionError:
        print("Crawling Failed", url)
        return None
