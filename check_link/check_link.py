from __future__ import absolute_import, unicode_literals
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
import requests as rq
import sys, traceback, json, time


all_link = set()
origin_host = ''

top_url = ''
ignore_urls = []

# Request Seesion for https retry.
rqs = None

# if same domain, INNER, otherwise OUTER.
(INNER, OUTER) = range(2)


def get_link_response(url, retry):
    #print(url)

    # It sets timeout '30' sec, because it takes 10-20 sec to GET 'https://maven.apache.org/install.html'.
    res = None
    try:
        res = rq.get(url, timeout=30, verify='/etc/ssl/certs/ca-certificates.crt')
        res.encoding = res.apparent_encoding
    except:
        if retry > 0:
           time.sleep(3)
           retry -= 1
           res = get_link_response(url, retry)
        else:
           raise Exception('Error max retry.')

    return res


def check_link():

    global all_link

    ### Top URL
    all_link.add((top_url, INNER))

    # links in Top URL Page.
    links = get_links(top_url, INNER)
    all_link |= links


    ### Child page
    while True:

        next_links = links.copy()
        links = set()

        for link_url, domain_type in next_links:
            links |= get_links(link_url, domain_type)

        if len(links) == 0:
            break

        all_link |= links

    ###print(all_link)


def get_links(url, domain_type):

    response = None

    try:
        # 指定されたURLをGETして解析
        response = get_link_response(url, 3)

        # Link Status OK?
        assert response.status_code == 200

    except AssertionError as e:
        print('Error link detected: ' + url)
        print

    except Exception as e:
        print('Response Error: ' + url)
        print(e)
        print


    # Empty Response, Outer domain  --> Non-Recursive
    if not response or domain_type == OUTER:
       return set()

    else:
       return collect_link(url, response.text, ('a', 'href'), ('img', 'src'))



def collect_link(base_url, html, *tag_attr_list):

    soup = BeautifulSoup(html, "lxml")
    link_url = ''
    links = set()


    def add_url_domain(url, domain_type):
        """
          Add url with domain_type, INNER or OUTER.
        """
        if (url, domain_type) not in all_link:
           links.add((url, domain_type))


    for tag, attr in tag_attr_list:

        for a in soup.find_all(tag):

            link_url = a.get(attr)
            domain = None

            if not link_url: continue

            if '://' + origin_host + '/' in link_url:
                # 同一ドメインかつ絶対パス
                domain = INNER

            elif link_url.find('://') > -1:
                # 外部サイトリンク
                domain = OUTER

            else:
                # 相対パス
                # --> 絶対パスに
                domain = INNER
                link_url = urljoin(base_url, link_url)


            if not link_url in ignore_urls:
               add_url_domain(link_url, domain)

    return links


def read_config(config_json):

    with open(config_json, 'r') as f:
        cj = json.load(f)

    return cj['top_url'], cj['ignore_urls']


if __name__ == '__main__':

    argvs = sys.argv

    top_url, ignore_urls = read_config(argvs[1])
    origin_host = urlparse(top_url).netloc

    #rqs = requests.Session()
    #rqs.max_redirects = 5
    #rqs.mount('https://', HTTPAdapter(max_retries=10))

    check_link()

