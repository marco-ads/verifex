import requests
import xml.etree.ElementTree as ET
from urllib.parse import quote


def find_similar_news(query: str, max_results: int = 5) -> list:
    if not query or len(query.strip()) < 5:
        return []
    try:
        q = quote(query[:100])
        url = f"https://news.google.com/rss/search?q={q}&hl=es&gl=MX&ceid=MX:es"
        resp = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"},
        )
        root = ET.fromstring(resp.content)
        items = root.findall(".//item")
        results = []
        for item in items[:max_results]:
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            pub_date = item.findtext("pubDate", "")
            source_el = item.find("source")
            source = source_el.text if source_el is not None else ""
            if title and link:
                results.append(
                    {
                        "title": title,
                        "url": link,
                        "published": pub_date,
                        "source": source,
                    }
                )
        return results
    except Exception:
        return []
