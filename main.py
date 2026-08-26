from extract import collect_page
from get_techs import get_techs
from playwright.sync_api import sync_playwright
import csv
from pathlib import Path
import json

def load_domains():
    file_path = (Path(__file__).resolve().parent/"part-00000-66e0628d-2c7f-425a-8f5b-738bcd6bf198-c000.csv")

    with file_path.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))

    return rows


domains = [domain["root_domain"] for domain in load_domains()]
domains = ["verticalcommunitychurch.com",
"gitesducharmois.fr",
"allegrocreditbeta.com",
"hoffmaninstitute.co.uk"]
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