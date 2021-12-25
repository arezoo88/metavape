import requests
import traceback
from lxml import etree
import time

request_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
}


def load_full_string(page_url):
    while True:
        try:
            response = requests.request(
                "GET", page_url, verify=False, timeout=60, headers=request_headers
            )
            response = response.text
            response = response.encode("utf-8")
            response = response.decode("utf-8")
            html_string = response
            return html_string
        except Exception as e:
            print(traceback.format_exc())
            print("Time out")


def get_data_from_xpath(html, x_paths, need_dom):
    dom = etree.HTML(html)
    stringify = etree.XPath("string()")
    result = {}
    for key in x_paths:
        result[key] = []
        try:
            tmp = dom.xpath(x_paths[key])
            try:
                if need_dom:
                    result[key] = tmp
                    continue
                for item in tmp:

                    try:
                        if type(item) == etree._Element:
                            result[key].append(stringify(item))
                        else:
                            result[key].append(item)
                    except:
                        print(traceback.format_exc())
                        result[key] = ["-"]
            except:
                print(traceback.format_exc())
                pass
        except:
            print(traceback.format_exc())
    return result


def get_data(url, xpaths, need_dom=False):
    time_1 = time.time()
    html = load_full_string(url)
    print("html", time.time() - time_1)
    data = get_data_from_xpath(html, xpaths, need_dom)
    return data


# xpath = {
#     "comment": '//*[@id="detail--product-reviews"]/div[contains(@class, "review--entry")]/div[@class="entry--content"]/p[contains(@class, "content--box")]',
#     "title": '//*[@id="detail--product-reviews"]/div[contains(@class, "review--entry")]/div[@class="entry--content"]/h4/text()',
# }


# url = "https://dampfdorado.de/liquid-cappuccino"
# data = get_data(url, xpath)
# print(data)
# info = {"body": data["comment"], "title": data["title"]}
# print(info)
