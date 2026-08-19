from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def collect_page(browser, domain):
    if not domain.startswith(("http://", "https://")):
        requested_url = f"https://{domain}"
    else:
        requested_url = domain

    # main data 
    page_data = {
        "input_domain": domain,
        "requested_url": requested_url,
        "final_url": None,
        "status_code": None,
        "title": None,
        "main_response_headers": {},
        "cookies": [],
        "raw_html": None,
        "rendered_html": None,
        "scripts": [],
        "meta_tags": [],
        "links": [],
        "network_requests": [],
        "network_responses": [],
        "error": None,
    }

    # new context for page
    context = browser.new_context(ignore_https_errors=True)

    page = context.new_page()

    # rulate automat mai jos
    def save_request(request):
        page_data["network_requests"].append({
            "url": request.url,
            "method": request.method,
            "resource_type": request.resource_type,
        })

    def save_response(response):
        page_data["network_responses"].append({
            "url": response.url,
            "status": response.status,
            "resource_type": response.request.resource_type,
            "headers": response.headers,
        })

    # aici rulate automat functiile de mai sus la fiecare apel/raspuns
    page.on("request", save_request)
    page.on("response", save_response)

    try:
        main_response = page.goto(
            requested_url,
            wait_until="domcontentloaded",
            timeout=30_000,
        )

        # wait time for js
        page.wait_for_timeout(3000)

        
        page_data["final_url"] = page.url
        page_data["title"] = page.title()

        if main_response is not None:
            page_data["status_code"] = main_response.status
            page_data["main_response_headers"] = (
                main_response.all_headers()
            )

            # raw html
            try:
                page_data["raw_html"] = main_response.text()
            except Exception:
                page_data["raw_html"] = None

        # rendered html
        page_data["rendered_html"] = page.content()

        # Toate tagurile <script>.                      # here we could use js to grab the elements from the html, faster but less readalbe for me rn
        soup = BeautifulSoup(
            page_data["rendered_html"],
            "html.parser"
        )

        for script in soup.find_all("script"):
            src = script.get("src")

            # grab source, if it has
            absolute_src = None
            if src is not None:
                absolute_src = urljoin(page.url, src)

            # grab in line code, if it has
            inline_text = None
            if src is None:
                inline_text = script.string or ""
                inline_text = inline_text[:1000]

            page_data["scripts"].append({
                "src_original": src,
                "src": absolute_src,
                "type": script.get("type"),
                "async": script.has_attr("async"),
                "defer": script.has_attr("defer"),
                "integrity": script.get("integrity"),
                "inline_text": inline_text,
            })
        


        # save meta tags
        for meta in soup.find_all("meta"):
            page_data["meta_tags"].append({
                "name": meta.get("name"),
                "property": meta.get("property"),
                "http_equiv": meta.get("http-equiv"),
                "content": meta.get("content"),
            })


        # Toate tagurile <link>.
        for link in soup.find_all("link"):
            href = link.get("href")

            absolute_href = None
            if href is not None:
                absolute_href = urljoin(page.url, href)

            page_data["links"].append({
                "href_original": href,
                "href": absolute_href,
                "rel": link.get("rel"),
                "type": link.get("type"),
                "as": link.get("as"),
                "integrity": link.get("integrity"),
            })

        page_data["cookies"] = context.cookies()

    except Exception as error:
        page_data["final_url"] = page.url
        page_data["error"] = str(error)

    finally:
        context.close()

    return page_data


def main():
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True
        )

        page_data = collect_page(
            browser,
            "katesworldtravel.com"
        )

        browser.close()

    print("Domeniu:", page_data["input_domain"])
    print("URL final:", page_data["final_url"])
    print("Status:", page_data["status_code"])
    print("Titlu:", page_data["title"])
    print("Scripturi:", len(page_data["scripts"]))
    print("Meta tags:", len(page_data["meta_tags"]))
    print("Link tags:", len(page_data["links"]))
    print("Requesturi:", len(page_data["network_requests"]))
    print("Răspunsuri:", len(page_data["network_responses"]))
    print("Cookies:", len(page_data["cookies"]))
    print("Eroare:", page_data["error"])


if __name__ == "__main__":
    main()