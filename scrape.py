from bs4 import BeautifulSoup
import urlparse 
from itertools import izip
import sys
import pickle

soup = BeautifulSoup(open(sys.argv[1]), 'html.parser')
body = soup.find(id="main_body")
tables = list(soup.find_all("table"))
recipe_table = tables[-1]


def pairwise(t):
    it = iter(t)
    return izip(it,it)

def get_item_id(link):
    parsed = urlparse.urlparse(link)
    return urlparse.parse_qs(parsed.query)["witem"][0]

def parse_item(quantity_string, link):
    item = {}
    item["name"] = link.string
    item["id"] = int(get_item_id(link['href']))
    stripped_string = quantity_string.replace(', ', '').replace('x', '').strip()
    item["quantity"] = int(stripped_string)
    return item

ir = 0
recipes = {}
for row in recipe_table.find_all("tr"):
    if (ir > 1):
        ic = 0
        recipe = {}
        no_output = False
        for col in row.find_all("td"):
            item = {}
            if (ic == 4):
                inputs = []
                mats = list(col.children)
                for q, l in pairwise(mats):
                    inputs.append(parse_item(q, l))
                recipe["inputs"] = inputs
            if (ic == 3):
                if col.string:
                    recipe["skill"] = int(col.string)
                else:
                    recipe["skill"] = 0
            if (ic == 5):
                if len(list(col.children)) == 0:
                    no_output = True
                    continue
                (quantity_string, link) = col.children
                recipe["output"] = parse_item(quantity_string, link)
            ic += 1
        if not no_output:
            recipes[recipe["output"]["id"]] = recipe
    ir += 1

output_filename = sys.argv[1].replace('.html', '')
sys.setrecursionlimit(10000)
with open(output_filename + '.pickle', 'wb') as handle:
    pickle.dump(recipes, handle, protocol=pickle.HIGHEST_PROTOCOL)

