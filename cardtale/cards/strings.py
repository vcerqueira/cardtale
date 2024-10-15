import json
from typing import List
from pathlib import Path

default_locale = 'en-gb'
cached_strings = {}

STRINGS_DIR = Path(__file__).parent.parent / 'cards' / 'templates' / 'strings'


def refresh():
    global cached_strings
    with open(f'{STRINGS_DIR}/{default_locale}.json') as f:
        cached_strings = json.load(f)


def gettext(name):
    return cached_strings[name]


def join_l(x: List[str], collapse_with: str = 'and') -> str:
    if len(x) == 1:
        xj = ''.join(x)
    elif len(x) == 0:
        xj = ''
    elif len(x) == 2:
        xj = f'{x[0]} and {x[1]}'
    else:
        xj = ', '.join(x[:-1]) + f', {collapse_with} {x[-1]}'

    return xj


refresh()
