"""B7 bookmarks — tests. Run: pytest test_markhive.py"""

NETSCAPE = """<!DOCTYPE NETSCAPE-Bookmark-file-1>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE><H1>Bookmarks</H1><DL><p>
<DT><A HREF="https://example.com" TAGS="dev,ai">Example</A>
<DT><A HREF="https://arxiv.org" TAGS="ai">arXiv</A>
</DL><p>"""


def test_parse_netscape():
    from bookmarks.bm.import_export import parse_netscape

    bms = parse_netscape(NETSCAPE)
    assert len(bms) == 2
    assert bms[0]["url"] == "https://example.com"
    assert "dev" in bms[0]["tags"]


def test_export_netscape():
    from bookmarks.bm.import_export import export_netscape

    xml = export_netscape([{"url": "https://x.com", "title": "X", "tags": ["dev"]}])
    assert "https://x.com" in xml and 'TAGS="dev"' in xml


def test_export_import_roundtrip():
    from bookmarks.bm.import_export import export_netscape, parse_netscape

    bms = [{"url": "https://a.com", "title": "A", "tags": ["t1"]}]
    assert parse_netscape(export_netscape(bms))[0]["url"] == "https://a.com"
