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
    
    url = page_data.get("final_url")
    if url:
        for app_name, app_spec in data["apps"].items():
                if "url" in app_spec:
                    if contains(url, app_spec["url"]):
                        print("url",app_name, app_spec)

    response_headers = page_data.get("main_response_headers")
    if response_headers:

        response_headers = {
            name.lower(): value
            for name, value in response_headers.items()
        }

        for app_name, app_spec in data["apps"].items():
            if "headers" in app_spec:
                for header_name, regex_rule in app_spec["headers"].items():
                    response_header_value = response_headers.get(header_name.lower())

                    if response_header_value:
                        detection_pattern = regex_rule.split("\\;", 1)[0]

                        compiled_regex = re.compile(
                            detection_pattern,
                            flags=re.IGNORECASE
                        )

                        match = compiled_regex.search(response_header_value)
                        if match:
                            print("headers",app_name, header_name,response_headers )



get_techs({"main_response_headers": {
    "content-type": "text/html; charset=UTF-8",
    "server": "cloudflare",
    "x-powered-by": "PHP/8.2",
    "set-cookie": "PHPSESSID=abc123; Path=/",
    "cache-control": "no-cache"
}})