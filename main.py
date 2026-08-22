from extract import collect_page
from get_techs import get_techs
from playwright.sync_api import sync_playwright

domains = ["largsbaychiropractic.com.au","38inspect.com",
"newbeaverborough.org"
]
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        headless=True
    )

    for domain in domains:
        page_data = collect_page(browser, domain)
        get_techs(page_data)
    browser.close()