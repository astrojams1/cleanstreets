import json
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
HTML_PATH = ROOT / "index.html"
ROBOTS_PATH = ROOT / "robots.txt"
SITEMAP_PATH = ROOT / "sitemap.xml"
CANONICAL_URL = "https://www.cleanstreets.io/"


@pytest.fixture(scope="module")
def soup():
    html = HTML_PATH.read_text(encoding="utf-8")
    return BeautifulSoup(html, "html.parser")


def test_canonical_and_hreflang_links(soup):
    canonical = soup.find("link", rel="canonical")
    assert canonical is not None, "Canonical link tag is missing"
    assert canonical.get("href") == CANONICAL_URL

    alternate = soup.find("link", rel="alternate", hreflang="en")
    assert alternate is not None, "hreflang alternate tag is missing"
    assert alternate.get("href") == CANONICAL_URL


def test_core_meta_tags(soup):
    description = soup.find("meta", attrs={"name": "description"})
    assert description is not None, "Meta description is missing"
    assert "community-supported" in description.get("content", "").lower()

    og_url = soup.find("meta", property="og:url")
    assert og_url is not None and og_url.get("content") == CANONICAL_URL

    twitter_card = soup.find("meta", attrs={"name": "twitter:card"})
    assert twitter_card is not None and twitter_card.get("content") == "summary_large_image"

    robots = soup.find("meta", attrs={"name": "robots"})
    assert robots is not None and "index" in robots.get("content", "")


def test_adsense_script_present(soup):
    script = soup.find("script", src=lambda value: value and "adsbygoogle.js?client=ca-pub-1558201460533095" in value)
    assert script is not None, "Updated AdSense script with client parameter is missing"
    assert script.get("crossorigin") == "anonymous"


def test_structured_data_graph(soup):
    ld_json_scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
    assert ld_json_scripts, "Structured data script not found"

    data = json.loads(ld_json_scripts[0].string)
    assert data.get("@context") == "https://schema.org"

    graph = data.get("@graph", [])
    assert graph, "Structured data @graph is empty"

    website = next((node for node in graph if node.get("@type") == "WebSite"), None)
    assert website is not None, "WebSite node missing from structured data"
    assert website.get("url") == CANONICAL_URL
    potential_action = website.get("potentialAction", {})
    assert potential_action.get("@type") == "DonateAction"

    organization = next((node for node in graph if node.get("@type") == "NGO"), None)
    assert organization is not None, "NGO node missing from structured data"
    assert "San Francisco" in organization.get("areaServed", "")
    assert "trash" in " ".join(organization.get("keywords", [])).lower()


def test_robots_txt_includes_sitemap():
    content = ROBOTS_PATH.read_text(encoding="utf-8").splitlines()
    assert "User-agent: *" in content
    assert any(line.strip().startswith("Sitemap:") for line in content)


def test_sitemap_urls():
    tree = ET.parse(SITEMAP_PATH)
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = {
        url.find("sm:loc", namespace).text
        for url in tree.getroot().findall("sm:url", namespace)
    }
    assert CANONICAL_URL in urls
    assert "https://www.cleanstreets.io/v1/index2.html" in urls
