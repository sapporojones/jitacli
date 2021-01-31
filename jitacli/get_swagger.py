import pickle

from esipy import EsiApp
from esipy import EsiClient
from esipy import App


esi_app = EsiApp()
app = esi_app.get_latest_swagger
pickle.dump(app, open("app.p", "wb"))
