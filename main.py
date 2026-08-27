from playwright.sync_api import sync_playwright
from pathlib import Path
import json

from extract import collect_page
from helpers import load_domains
from get_techs import get_techs


domains = [domain["root_domain"] for domain in load_domains()]

all_results = []

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=True
    )

    for domain in domains:
        print(domain)
        page_data = collect_page(browser, domain)

        page_results = get_techs(page_data)

        all_results.append(page_results)

    browser.close()





total_detections = sum(len(page["technologies"]) for page in all_results)

unique_technologies = set()

for page in all_results:
    unique_technologies.update(page["technologies"].keys())

output_data = {
    "summary": {
        "websites": len(all_results),
        "total_detections": total_detections,
        "unique_technologies": len(unique_technologies),
    },
    "results": all_results,
}



file_path = (Path(__file__).resolve().parent/"results.json")
with file_path.open( "w", encoding="utf-8") as file:
    json.dump( output_data, file, indent=2, ensure_ascii=False)