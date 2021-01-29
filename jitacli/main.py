# requests is necessary for us to perform queries against
# CCP's myriad ESI endpoints
import requests


# importing tqdm because for loops are slow and we want
# to show progress to the user in some way
import tqdm

#importing rich for output prettification
import rich
from rich.traceback import install
install()


def get_itemid(item_name):
    # take item name, search esi for item_id, return id for
    # later use in the "program"
    item_id = requests.get('https://esi.evetech.net/latest/search/', params={
        'categories': 'inventory_type',
        'search': item_name,
        'strict': True,
    })
    print(item_id)
    return item_id


def get_itemvalue(item_id):
    price_list = []
    query_url = f"https://esi.evetech.net/latest/markets/10000002/orders/?datasource=tranquility&order_type=sell&page=1&type_id={item_id}"
    order_request = requests.get(query_url)
    order_text = order_request.json()
    print(order_text)

    i = 1

    # for x in order_list:
    #     print(order_list[i]['system_id'])
    #     if order_list[i]["system_id"] == "30000142":
    #         print(order_list[i]["price"])
    #         price_list.append(int(order_list[i]["price"]))
    #         i += 1
    #     else:
    #         i += 1
    return #min(price_list)


def make_list():
    # this function makes the shopping list out of a shopping list file
    # the file should be single item per line format
    shopping_list = []
    with open('shopping_list') as f:
        for item in f.read().splitlines():
            shopping_list.append(item.upper())

    return shopping_list


if __name__ == "__main__":
    cleaned_list = make_list()
    output_name = []
    output_price = []

    for x in cleaned_list:
        get_id = get_itemid(x)
        price = get_itemvalue(get_id)
        output_name.append(x)
        output_price.append(price)
    print(output_price)
    #final_list = zip(output_name,output_price)
    # rich.print(final_list)

