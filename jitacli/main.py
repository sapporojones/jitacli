# requests is necessary for us to perform queries against
# CCP's myriad ESI endpoints
import requests

# import regex
import re

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed


# importing tqdm because for loops are slow and we want
# to show progress to the user in some way
import tqdm

# importing rich for output prettification
from rich import print
from rich.traceback import install

install()


def get_itemid(item_name):
    # take item name, search esi for item_id, return id for
    # later use in the "program"
    try:
        item_id_get = requests.get(
            "https://esi.evetech.net/latest/search/",
            params={
                "categories": "inventory_type",
                "search": item_name,
                "strict": True,
            },
        )
        item_id_json = item_id_get.json()
        # print(item_id_json['inventory_type'])
        item_id = item_id_json["inventory_type"]
        # print(item_id[0])
        retval = item_id[0]
    except:
        retval = 0
    return retval


def get_itemvalue(item_id):
    price_list = []
    query_url = f"https://esi.evetech.net/latest/markets/10000002/orders/?datasource=tranquility&order_type=sell&page=1&type_id={item_id}"
    order_request = requests.get(query_url)
    order_list = order_request.json()
    i = 0
    for x in order_list:
        # print(order_list[i]['system_id'])
        if order_list[i]["system_id"] == 30000142:
            # print(order_list[i]["price"])
            price_list.append(order_list[i]["price"])
            i += 1
        else:
            i += 1
    # print(price_list)
    lowest_jita = min(price_list)
    return lowest_jita


def make_list():
    # this function makes the shopping list out of a shopping list file
    # the file should be single item per line format
    shopping_list = []
    with open("shopping_list") as f:
        for item in f.read().splitlines():

            if "[" in item:
                pass
            elif item[0:] == "":
                pass
            else:
                shopping_list.append(item.upper())

    return shopping_list


if __name__ == "__main__":
    cleaned_list = make_list()
    output_name = []
    output_price = []
    total_price = 0
    id_list = []

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_result = executor.map(get_itemid, cleaned_list)

        for future in future_result:
            id_list.append(future)

    with ThreadPoolExecutor(max_workers=20) as executor:
        future_result = executor.map(get_itemvalue, id_list)

        for future in future_result:
            # price.append(future)
            # print(future)
            total_price += future

    # for x in cleaned_list:
    #     # get_id = get_itemid(x)
    #
    #     # price = get_itemvalue(get_id)
    #     output_name.append(x)
    #     output_price.append(price)
    #     total_price += price
    #     print(f"The lowest Jita sell price for {x.title()} is {price}")
    cleaned_price = "{:,}".format(total_price)
    print(f"The total Jita sell price for this would be {cleaned_price}")
