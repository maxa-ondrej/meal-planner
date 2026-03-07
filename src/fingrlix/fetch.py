import urllib.request
import os
from bs4 import BeautifulSoup
from enum import Enum

class Batch(Enum):
    MO_TU = "pondeli-utery", 2
    WE_TH = "streda-ctvrtek", 2
    FR_SA_SU = "patek-sobota-nedele", 3
    
    @property
    def url_part(self):
        return self.value[0]
    
    @property
    def meals_count(self):
        return self.value[1]


def fetch(week: int, batch: Batch):
    url = f"https://www.fingrlix.com/vyber-jidla/{batch.url_part}?week={week}"
    file = f"week{week}.html"
    urllib.request.urlretrieve(url, file)
    with open(file) as f:
        html = f.read()
        soup = BeautifulSoup(html, "html.parser")
    os.remove(file)
    return soup