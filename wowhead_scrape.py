import sys, re
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

WOWHEAD_ITEM_PREFIX_URL = "https://classic.wowhead.com/item="

def simple_get(url):
    try:
        with closing(get(url, stream=True)) as resp:

            print(resp.elapsed.total_seconds())
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200 
            and content_type is not None 
            and content_type.find('html') > -1)


def log_error(e):
    print(e)

def parse_money(node, moneyclass):
    money_node = node.find("span", attrs={"class", moneyclass})
    if money_node is not None:
        return int(money_node.text)
    return 0


def scrape_item(item_id):
    item = {}
    item["id"] = item_id
    raw_html = simple_get(WOWHEAD_ITEM_PREFIX_URL+item_id)
    soup = BeautifulSoup(raw_html, 'html.parser')
    item["name"] = soup.find("h1").text
    item_level_match = re.search("Item Level <!--ilvl-->(\d+)<", raw_html)
    if item_level_match is not None:
        item["level"] = int(item_level_match.group(1))
    else:
        item["level"] = None
    vendor_sell_node = soup.find("div", attrs={"class":"whtt-sellprice"})
    if vendor_sell_node is not None:
        vsell_copper = parse_money(vendor_sell_node, "moneycopper")
        vsell_silver = parse_money(vendor_sell_node, "moneysilver")
        vsell_gold = parse_money(vendor_sell_node, "moneygold")
        item["vendor_sell"] = vsell_copper + vsell_silver * 100 + vsell_gold * 1000
    else:
        item["vendor_sell"] = None
    buy_price_match = re.search("Cost: \[money=(\d+)-(\d+)\]", raw_html)
    if buy_price_match is not None:
        item["vendor_buy_min"] = int(buy_price_match.group(1))
        item["vendor_buy_max"] = int(buy_price_match.group(2))
    else:
        item["vendor_buy_min"] = None
        item["vendor_buy_max"] = None
    max_stack_match = re.search("Max Stack: (\d+)<", raw_html)
    if max_stack_match is not None:
        item["max_stack"] = max_stack_match.group(1)
    else:
        item["max_stack"] = None
    return item

