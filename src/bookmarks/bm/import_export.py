from bs4 import BeautifulSoup

def parse_netscape(html):
    soup = BeautifulSoup(html, "html.parser")
    out = []
    for a in soup.find_all("a", href=True):
        tags = (a.get("tags") or "").split(",")
        out.append({"url": a["href"], "title": a.get_text(strip=True) or a["href"], "tags": [t for t in tags if t]})
    return out

def export_netscape(bookmarks):
    lines = ['<!DOCTYPE NETSCAPE-Bookmark-file-1>', '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
             '<TITLE>Bookmarks</TITLE><H1>Bookmarks</H1><DL><p>']
    for b in bookmarks:
        tags = ",".join(b.get("tags", []))
        lines.append(f'<DT><A HREF="{b["url"]}" TAGS="{tags}">{b.get("title", "")}</A>')
    lines.append("</DL><p>")
    return "\n".join(lines)
