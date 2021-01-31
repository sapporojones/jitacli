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
import jitacli.main as j



client = EsiClient(
    retry_requests=True,  # set to retry on http 5xx error (default False)
    headers={"User-Agent": "rando eve user just lookin at stuff"},
    raw_body_only=False,  # default False, set to True to never parse response and only return raw JSON string content.
)


esi_app = EsiApp()
# dir_path = os.path.dirname(os.path.realpath(__file__))
# pickled_obj_path = os.path.join(dir_path, "app.p")
#
# app = pickle.load(open(pickled_obj_path, "rb"))


def test_get_itemid():
    name = "Ibis"
    id = j.get_itemid(name)
    assert id == 601


def test_get_itemvalue():
    item_id = 601
    quantity = 1
    item_name = "Ibis"
    x = j.get_itemvalue(item_id, quantity, item_name)
    assert x > 0

def test_q_list():
    cleaned_item_list = []
    swap_list = []
    quant_list_rdy = []
    itemlist = ["Kronos","Null L x2820"]

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
    assert quant_list_rdy[1] == 2820