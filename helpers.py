import json
import os
from urllib.parse import  urlsplit, urlunsplit
import csv

def load_apps(filename="apps.json"):

    filename = os.path.join(os.path.dirname(__file__),filename)

    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)

def load_wordpress_components(filename="wordpress_components.json"):

    filename = os.path.join(os.path.dirname(__file__),filename)

    with open(filename, "r", encoding="utf-8") as file:
        return json.load(file)
    
def load_domains(filename="part-00000-66e0628d-2c7f-425a-8f5b-738bcd6bf198-c000.csv"):
    filename = os.path.join(os.path.dirname(__file__),filename)

    with open(filename, "r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))
    
    
def sanitize_url(url):
    parsed_url = urlsplit(url)

    sanitized_url = urlunsplit(( 
        parsed_url.scheme,
        parsed_url.netloc,
        parsed_url.path,
        "",
        ""
    ))
    return sanitized_url
