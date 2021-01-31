# requests is necessary for us to perform queries against
# CCP's myriad ESI endpoints
import requests
from os import system, name
# import regex
import re
import pickle
from concurrent.futures import ThreadPoolExecutor
# importing tqdm because for loops are slow and we want
# to show progress to the user in some way
from tqdm import tqdm
# importing rich for output prettification
from rich.console import Console
c = Console()
# import rich
from rich.traceback import install
from esipy import EsiApp
from esipy import EsiClient
import pandas as pd
from time import sleep

install()


client = EsiClient(
    retry_requests=True,  # set to retry on http 5xx error (default False)
    headers={"User-Agent": "rando eve user just lookin at stuff"},
    raw_body_only=False,  # default False, set to True to never parse response and only return raw JSON string content.
)


esi_app = EsiApp()

# app = esi_app.get_latest_swagger

price_list_df = []
item_list_df = []
quant_list_rdy = []
swap_list = []
cleaned_item_list = []
quant_testing = []


def clear_screen():
    # for windows
    if name == "nt":
        _ = system("cls")
    # for mac and linux(here, os.name is 'posix')
    else:
        _ = system("clear")

# never know, one day you may need to translate some ids to names...
# def get_name(item_id):
#     # take item name, search esi for item_id, return id for
#     # later use in the "program"
#     item_list = []
#     item_list.append(item_id)
#     data = {"ids": item_list}
#     item_names = app.op['post_universe_names'](
#         ids=item_list
#     )
#
#     response = client.request(item_names)
#
#     retval = response.data[0].name
#
#     # print(f"get_name: response.data = {response.data}")
#
#     return retval


def get_itemid(item_name):
    # take item name, search esi for item_id, return id for
    # later use in the "program"
    try:
        # sleep(.05)
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

        # print(f"get_itemid: retval = {retval} searched for {item_name}")

    except:
        retval = 0
    return retval


def get_itemvalue(item_id, quantity, item_name):
    """
    Create and add to global lists
    :param item_id: takes item_id and returns value
    :return:
    """
    # sleep(.05)
    price_list = []
    query_url = f"https://esi.evetech.net/latest/markets/10000002/orders/?datasource=tranquility&order_type=sell&page=1&type_id={item_id}"
    order_request = requests.get(query_url)
    order_list = order_request.json()
    i = 0
    for x in order_list:

        # print(order_list[i]['system_id'])

        if order_list[i]["system_id"] == 30000142:

            # print(order_list[i]["price"])

            price_list.append(int(order_list[i]["price"]))
            i += 1
        else:
            i += 1

    # print(f"get_itemvalue: item_id = {item_id}")

    # item_name = get_name(item_id)

    item_list_df.append(item_name)
    lowest_jita_raw = min(price_list)
    final_price_r = int(lowest_jita_raw) * quantity
    quant_testing.append(quantity)
    final_price = f"{final_price_r:,}"
    # sleep(.05)
    # c.print(f"Jita Sell Value for {item_name} is {cleaned_price}", style="bold white")

    price_list_df.append(final_price)
    return final_price_r


def q_list(itemlist):
    """
    I need a third list for parsed quantities it turns out
    I'm just going to lazily do the global list workaround
    instead of passing lists around endlessly.
    :param itemlist: List of lines from the shopping list file
    :return:builds the global quantity list and returns
    """
    for line in itemlist:
        re_search = re.search(r"[x]\d", line)
        if re_search is not None:
            splitline = line.split("x", 20)
            quant = splitline[-1]
            quant_list_rdy.append(int(quant))
            swap_list.append(splitline[0])
            strip_tot = len(quant) + 2
            cleaned_item_list.append(line[:-strip_tot])
        else:
            quant_list_rdy.append(int(1))
            swap_list.append(line)
            cleaned_item_list.append(line)
    return


def make_list():
    # this function makes the shopping list out of a shopping list file
    # the file should be single item per line format
    shopping_list = []
    parse_title = []
    with open("shopping_list") as f:
        for item in f.read().splitlines():

            if "[" in item:

                if "[EMPTY" in item.upper():
                    pass
                else:
                    parse_title = item
                    lb = parse_title.strip("[")
                    rb = lb.strip("]")
                    cl = rb.split(",", 1)
                    final = cl[0]
                    shopping_list.append(final)

            elif "," in item:
                grp_item = item.split(",", 1)
                shopping_list.append(grp_item[0])
                shopping_list.append(grp_item[1])

            elif "/OFFLINE" in item:
                shopping_list.append(item[:-9])

            elif item[0:] == "":
                pass
            else:
                shopping_list.append(item)

    return shopping_list


if __name__ == "__main__":
    app = pickle.load(open("app.p", "rb"))
    clear_screen()
    dirty_list = make_list()
    clear_screen()
    tqdm(q_list(dirty_list))
    clear_screen()
    output_name = []
    output_price = []
    total_price = 0
    id_list = []

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_result = executor.map(get_itemid, cleaned_item_list)
        with tqdm(total=(len(cleaned_item_list))) as pbar:
            for future in future_result:
                id_list.append(future)
                pbar.update(1)
    # sleep(0.5)
    clear_screen()
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_result = executor.map(
            get_itemvalue, id_list, quant_list_rdy, cleaned_item_list
        )
        with tqdm(total=(len(cleaned_item_list))) as pbar:
            for future in future_result:
                total_price += future
                pbar.update(1)
    # sleep(1)
    clear_screen()
    df1 = pd.DataFrame(
        {
            "Item Name": item_list_df,
            "Item Quantity": quant_testing,
            "Price": price_list_df,
        }
    )
    df1.sort_values(
        by="Price",
    )
    print(df1)
    cleaned_price = f"{total_price:,}"
    c.print(
        f"The total Jita sell price for this would be {cleaned_price}",
        style="bold white",
    )
