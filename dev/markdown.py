import os
import json
import logging
from substrate import Substrate, ComputeText, sb, ComputeJSON, RunPython

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load configuration
CONFIG_FILE = os.path.expanduser('~/.config/substrate/config.json')

def load_config():
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

config = load_config()
api_key = config['api_key']

substrate = Substrate(api_key=api_key)

def markdown(url: str):
    print(url)
    import requests
    from bs4 import BeautifulSoup
    from markdownify import markdownify

    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    return markdownify(str(soup))

response_1 = ComputeText(prompt="generate a random word.")

md = RunPython(
    function=markdown,
    kwargs={
        "url": sb.format("https://metrograph.com/film/?vista_film_id=9999001208&{foo}", foo=response_1.future.text)
    },
    pip_install=["requests", "beautifulsoup4", "markdownify"],
)
res = substrate.run(md)
out = res.get(md)
print(out.stdout) # (markdown content of the web page)