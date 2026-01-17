import urllib.request
import os
from bs4 import BeautifulSoup


def fetch(week: int):
    url = f"https://www.fingrlix.com/vyber-jidla/patek-sobota-nedele?week={week}"
    file = f"week{week}.html"
    urllib.request.urlretrieve(url, file)
    with open(file) as f:
        html = f.read()
        soup = BeautifulSoup(html, "html.parser")
    os.remove(file)
    return soup