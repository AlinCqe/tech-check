import get_techs

from get_techs import extract_wordpress_component
from helpers import sanitize_url


def test_sanitize_url_removes_query_and_fragment():
    url = "https://example.com/app.js?key=secret#section"

    result = sanitize_url(url)

    assert result == "https://example.com/app.js"


def test_extract_wordpress_plugin():
    url = ("https://example.com/wp-content/plugins/elementor/assets/app.js")

    result = extract_wordpress_component(url, "plugins")

    assert result == "elementor"


def test_extract_wordpress_theme():
    url = ("https://example.com/wp-content/themes/astra/assets/style.css")

    result = extract_wordpress_component(url, "themes")

    assert result == "astra"


def test_returns_none_for_non_wordpress_url():
    url = "https://example.com/assets/app.js"

    result = extract_wordpress_component(url, "plugins")

    assert result is None


def test_header_detection_redacts_cookie(monkeypatch):
    fake_apps = {
        "apps": {
            "PHP": {
                "headers": {
                    "Set-Cookie": "PHPSESSID="
                }
            }
        }
    }

    monkeypatch.setattr( get_techs,"apps_data",fake_apps )

    monkeypatch.setattr(get_techs,"wordpress_components", {"plugins": {},"themes": {} })

    page_data = {
        "input_domain": "example.com",
        "final_url": "https://example.com",
        "main_response_headers": {
            "Set-Cookie": "PHPSESSID=secret-value; Path=/"
        },
        "raw_html": None,
        "rendered_html": None,
        "scripts": [],
        "links": [],
        "network_requests": [],
    }

    result = get_techs.get_techs(page_data)

    proof = result["technologies"]["PHP"]["proof"]

    assert proof["source"] == "response_headers"
    assert proof["matched"] == "PHPSESSID=[REDACTED]"
    assert "secret-value" not in proof["matched"]


def test_network_script_detection_sanitizes_url( monkeypatch):
    fake_apps = {
        "apps": {
            "Example Analytics": {
                "script": "tracker\\.js"
            }
        }
    }

    monkeypatch.setattr(get_techs,"apps_data", fake_apps)
    monkeypatch.setattr(get_techs, "wordpress_components", {"plugins": {}, "themes": {}})

    page_data = {
        "input_domain": "example.com",
        "final_url": "https://example.com",
        "main_response_headers": {},
        "raw_html": None,
        "rendered_html": None,
        "scripts": [],
        "links": [],
        "network_requests": [
            {
                "url": (
                    "https://analytics.example.com/"
                    "tracker.js?api_key=secret"
                ),
                "resource_type": "script",
            }
        ],
    }

    result = get_techs.get_techs(page_data)

    proof = result[
        "technologies"
    ]["Example Analytics"]["proof"]

    assert proof["source"] == "network_script"
    assert proof["url"] == ( "https://analytics.example.com/tracker.js")
    assert "secret" not in proof["url"]