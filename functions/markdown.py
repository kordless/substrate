import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md

pip_install_strings = ["markdownify", "bs4"]

def substrate_function(func):
    func.is_substrate_function = True
    return func

@substrate_function
def markdown(url: str):
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    return md(str(soup))
