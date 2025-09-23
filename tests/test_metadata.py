import json
import re
from pathlib import Path

import pytest

HTML_PATH = Path(__file__).resolve().parents[1] / "index.html"
HTML = HTML_PATH.read_text(encoding="utf-8")


def test_canonical_link_points_to_primary_domain():
    assert 'rel="canonical"' in HTML, "Canonical link tag is missing"
    assert 'https://www.cleanstreets.io/' in HTML, "Canonical link should target the primary domain"


def test_key_meta_tags_present():
    required_selectors = [
        r'<meta[^>]+property="og:title"',
        r'<meta[^>]+name="twitter:card"',
        r'<meta[^>]+name="description"',
        r'<meta[^>]+property="og:image"',
    ]
    for selector in required_selectors:
        assert re.search(selector, HTML, flags=re.IGNORECASE), f"Expected meta tag matching {selector}"


def test_jsonld_contains_required_entities():
    match = re.search(r'<script type="application/ld\+json">(.*?)</script>', HTML, flags=re.DOTALL)
    assert match, "Structured data script tag not found"
    data = json.loads(match.group(1))
    assert "@graph" in data, "Structured data should include an @graph"
    types = {node.get("@type") for node in data["@graph"]}
    assert {"NGO", "Service", "FAQPage"}.issubset(types), "Structured data nodes are incomplete"


def test_adsense_snippet_uses_client_id():
    assert "adsbygoogle.js?client=ca-pub-1558201460533095" in HTML
    assert "data-full-width-responsive" in HTML


@pytest.mark.parametrize(
    "text",
    [
        "Mission District",
        "Volunteer activations",
        "Share Clean Streets",
    ],
)
def test_page_contains_high_intent_keywords(text):
    assert text in HTML
