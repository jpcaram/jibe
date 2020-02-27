from jinja2 import Template, Environment, DictLoader
from pathlib import Path

path = Path(__file__).parent.absolute()
with open(f'{path}/page.html') as f:
    html = f.read()
htmlt = Template(html)
