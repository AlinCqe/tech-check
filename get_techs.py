import os
import re
import json


def load_apps(filename="apps.json"):

    filename = os.path.join(os.getcwd(), os.path.dirname(__file__), filename)
    return json.load(open(filename))


def get_techs(page_data: dict):
    
    url = page_data.get("final_url")
    response_headers = page_data.get("main_response_headers")

    raw_html = page_data.get("raw_html")
    rendered_html = page_data.get("remdered_html")


    if url:
        for app_name, app_spec in data["apps"].items():
                if "url" in app_spec:

                    detection_pattern = app_spec["url"].split(r"\;", 1)[0]

                    compiled_regex = re.compile(
                        detection_pattern,
                        flags=re.IGNORECASE
                    )

                    match = compiled_regex.search(url)
                    if match:
                        print("url",app_name,url )


    
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


    #html both raw and 
    for html in raw_html, rendered_html:

        if not html:
            continue

        for key in "html", "script":
            for app_name, app_spec in data["apps"].items():

                html_snippets = app_spec.get(key, [])
                if not isinstance(html_snippets, list):
                    html_snippets = [html_snippets]
                
                for detection_pattern in html_snippets:
                    detection_pattern = detection_pattern.split("\\;", 1)[0]
                    compiled_regex = re.compile(
                        detection_pattern,
                        flags=re.IGNORECASE
                    )
                    match = compiled_regex.search(html)
                    if match:
                        print("html",app_name)

    # meta tags in same html loop
        meta_regex = re.compile(
            "<meta[^>]*?name=['\"]([^>]*?)['\"][^>]*?content=['\"]([^>]*?)['\"][^>]*?>",
            re.IGNORECASE
        )
        metas = dict(meta_regex.findall(html))
        
        for app_name, app_spec in data["apps"].items():
            for name, content in app_spec.get("meta", {}).items():
                if name in metas:
                                    
                    detection_pattern = content.split("\\;", 1)[0]
                    compiled_regex = re.compile(
                        detection_pattern,
                        flags=re.IGNORECASE
                    )
                    match = compiled_regex.search(metas[name])

                    break