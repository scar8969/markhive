import urllib.request, re
from bs4 import BeautifulSoup

def fetch_meta(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "bookmarks/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            html = r.read(1024 * 512).decode("utf-8", "ignore")
    except Exception:
        return {"title": url, "description": "", "favicon": "", "snapshot": ""}
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title else url
    desc = ""
    m = soup.find("meta", attrs={"name": "description"})
    if m:
        desc = m.get("content", "")
    favicon = ""
    icon = soup.find("link", rel=re.compile("icon", re.I))
    if icon:
        favicon = urllib.parse.urljoin(url, icon.get("href", ""))
    return {"title": title[:200], "description": desc[:500], "favicon": favicon,
            "snapshot": soup.get_text()[:2000]}
