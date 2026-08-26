import os
import re
import json
from urllib.parse import urlparse, urlsplit, urlunsplit

def load_apps(filename="apps.json"):

    filename = os.path.join(os.getcwd(), os.path.dirname(__file__), filename)
    return json.load(open(filename))

def extract_wordpress_component(resource_url, component_type):
    path = urlparse(resource_url).path
    parts = [part for part in path.split("/") if part]

    sequence = ["wp-content", component_type]

    sequence_length = len(sequence)

    for index in range(len(parts) - sequence_length):
        current_sequence = parts[index:index + sequence_length]

        if current_sequence == sequence:
            component_index = index + sequence_length
            return parts[component_index]
        
    return None


data = load_apps()
total_techs = {}

def get_techs(page_data: dict) -> dict :  
   
    page_result = {
        "link": page_data.get("input_domain"),
        "technologies": {}
    }

    url = page_data.get("final_url")
    response_headers = page_data.get("main_response_headers")
    raw_html = page_data.get("raw_html")
    rendered_html = page_data.get("rendered_html")
    page_scripts = page_data["scripts"];
    page_links = page_data["links"];
    network_requets = page_data.get("network_requests", [])

    # URL tech detection
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
                        
                        if app_name not in page_result["technologies"]:          #only adds proof if the tech isnt alredy saved
                            page_result["technologies"][app_name] = {
                                "proof": {
                                    "source": "initial url",
                                    "matched": url,
                                }
                            }

    # Response Headers tech detection
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
                            
                            if app_name not in page_result["technologies"]:          #only adds proof if the tech isnt alredy saved
                                page_result["technologies"][app_name] = {
                                    "proof": {
                                        "source": "response_headers",
                                        "matched": response_header_value,
                                    }
                                }

    #HTML both raw and rendered tech detection 
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
                        
                        if app_name not in page_result["technologies"]:          #only adds proof if the tech isnt alredy saved
                            page_result["technologies"][app_name] = {
                                "proof": {
                                    "source": "html",
                                    "matched": match.group(0)[:300]
                                }
                            }
    # meta tags detection in same html loop
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
                    if match:
                        
                        if app_name not in page_result["technologies"]:          #only adds proof if the tech isnt alredy saved
                            page_result["technologies"][app_name] = {
                                "proof": {
                                    "source": "meta tags",
                                    "matched": match.group(0)[:300]
                                }
                            }
                        break


    # #requests tech detection 
    for request in network_requets:
        request_url = request.get("url")
        resource_type = request.get("resource_type")

        if not request_url:
            continue


        if resource_type == "script":
              for app_name, app_spec in data["apps"].items():
                    script_patterns = app_spec.get("script", [])

                    if not isinstance(script_patterns, list):
                        script_patterns = [script_patterns]

                    for detection_pattern in script_patterns:
                        detection_pattern = detection_pattern.split(r"\;",1)[0]

                        compiled_regex = re.compile(detection_pattern ,flags=re.IGNORECASE)

                        match = compiled_regex.search(request_url)

                        if match:
                            
                            if app_name not in page_result["technologies"]:         #only adds proof if the tehc isnt alredy saved
                                page_result["technologies"][app_name] = {
                                    "proof": {
                                        "source": "network_script",
                                        "url": request_url,
                                    }
                                }  
                            break


    # saves all links from html and network requests
    resource_urls = []
    
    for script in page_data.get("scripts", []):
        script_url = script.get("src")

        if script_url:
            resource_urls.append({
                "url": script_url,
                "source": "script tag"
            })

    for link in page_data.get("links", []):
        link_url = link.get("href")

        if link_url:
            resource_urls.append({
                "url": link_url,
                "source": "link tag"
            })

    for request in page_data.get("network_requests", []):
        request_url = request.get("url")

        if request_url:
            resource_urls.append({
                "url": request_url,
                "source": "network request"
            })
            
    # checks for wdpress plugins or themes 
        
    for resource in resource_urls:
        resource_link = resource.get("url")
        resource_source = resource.get("source")
        if not resource_link:
            continue

        plugin_name = extract_wordpress_component(
            resource_link,
            "plugins"
        )

        if plugin_name:
            technology_name = f"WordPress Plugin: {plugin_name}"

            if technology_name not in page_result["technologies"]:
                page_result["technologies"][technology_name] = {
                    "proof": {
                        "source": resource_source,
                        "url": resource_link
                    }
                }

        theme_name = extract_wordpress_component(
            resource_link,
            "themes"
        )

        if theme_name:
            technology_name = f"WordPress Theme: {theme_name}"

            if technology_name not in page_result["technologies"]:
                page_result["technologies"][technology_name] = {
                    "proof": {
                        "source": resource_source,
                        "url": resource_link
                    }
                }

    return page_result