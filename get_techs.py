import os
import re
import json

def decode_bytes(data):
    """Decode bytes to string, trying multiple common encodings ?????""" 
    if not isinstance(data, bytes):
        return data
    
    for encoding in ['utf-8', 'iso-8859-1', 'windows-1252', 'latin-1']:
        try:
            return data.decode(encoding)
        except (UnicodeDecodeError, AttributeError):
            continue

    return data.decode('utf-8', errors='replace')


def load_apps(filename="apps.json"):

    filename = os.path.join(os.getcwd(), os.path.dirname(__file__), filename)
    return json.load(open(filename))


data = load_apps()
def contains(v, regex):
    """Removes meta data from regex then checks for a regex match"""
    v = decode_bytes(v)
    return re.compile(regex.split("\\;")[0], flags=re.IGNORECASE).search(v)

def get_techs(page_data: dict):
    
    url = page_data["final_url"]
    for app_name, app_spec in data["apps"].items():
            if "url" in app_spec:
                if contains(url, app_spec["url"]):
                    print("url",app_name, app_spec)

