import random
import re
import string
import requests

from bs4 import BeautifulSoup

def create_strings_from_file(filename, count):
    """
        Create all strings by reading lines in specified files
    """

    strings = []

    with open(filename, 'r', encoding="utf8") as f:
#         lines = [l.strip()[0:200] for l in f.readlines()]
        lines = [l.replace('\n','')[0:200] for l in f.readlines()]
        if len(lines) == 0:
            raise Exception("No lines could be read in file")
        while len(strings) < count:
            if len(lines) >= count - len(strings):
                strings.extend(lines[0:count - len(strings)])
            else:
                strings.extend(lines)

    return strings


