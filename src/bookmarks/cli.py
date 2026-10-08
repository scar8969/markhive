"""Command line front-end for the bookmarks service.

Flask, SQLAlchemy, requests and BeautifulSoup are imported lazily inside the
function that needs them, so ``python cli.py --help`` works on a machine where
the web dependencies are not installed yet.
"""
import argparse
import json
import sys

def _app():
    """Import the Flask app and push an application context for the caller."""
    try:
        from ._app import app
    except ModuleNotFoundError as exc:
        print("error: cannot import the application (%s)" % exc, file=sys.stderr)
        print("hint: install the requirements first: pip install -r requirements.txt", file=sys.stderr)
        raise SystemExit(2)
    ctx = app.app_context()
    ctx.push()
    return ctx

def _models():
    from .models import Bookmark, Tag, db
    return Bookmark, Tag, db

def _tag(Tag, name):
    """Reuse an existing tag row instead of creating a duplicate name."""
    return Tag.query.filter_by(name=name).first() or Tag(name=name)

def cmd_list(args):
    ctx = _app()
    try:
        Bookmark, Tag, db = _models()
        query = Bookmark.query
        if args.tag:
            query = query.filter(Bookmark.tags.any(Tag.name == args.tag))
        rows = query.order_by(Bookmark.id.desc()).limit(args.limit).all()
        if args.json:
            print(json.dumps([{"id": b.id, "title": b.title, "url": b.url,
                              "tags": [t.name for t in b.tags]} for b in rows], indent=2))
        else:
            for b in rows:
                print("%-4s %-48s %s" % (b.id, b.title[:48], b.url))
            print("-- %d bookmark(s)" % len(rows))
    finally:
        ctx.pop()
    return 0

def cmd_add(args):
    from .bm.fetch import fetch_meta
    ctx = _app()
    try:
        Bookmark, Tag, db = _models()
        if Bookmark.query.filter_by(url=args.url).first():
            print("error: already saved: %s" % args.url, file=sys.stderr)
            return 1
        meta = fetch_meta(args.url)
        bm = Bookmark(url=args.url, title=meta.get("title") or args.url,
                      description=meta.get("description", ""),
                      favicon=meta.get("favicon", ""),
                      snapshot=meta.get("snapshot", ""))
        for name in args.tags or []:
            bm.tags.append(_tag(Tag, name.strip()))
        db.session.add(bm)
        db.session.commit()
        print("added #%s: %s" % (bm.id, bm.title))
    finally:
        ctx.pop()
    return 0

def cmd_search(args):
    # search() touches db.session, so it needs the same pushed app context the
    # other subcommands use -- without it SQLAlchemy raises
    # "RuntimeError: Working outside of application context".
    from .bm.search import search
    ctx = _app()
    try:
        rows = search(args.query, tag=args.tag or "", limit=args.limit)
    finally:
        ctx.pop()
    if args.json:
        print(json.dumps(rows, indent=2))
    else:
        for row in rows:
            print("%-4s %-48s %s" % (row["id"], row["title"][:48], row["url"]))
        print("-- %d hit(s)" % len(rows))
    # No hits is a failed lookup: exit non-zero so a script can branch on it,
    # unless the caller passed --quiet.
    if not rows and not args.quiet:
        return 1
    return 0

def cmd_tags(args):
    ctx = _app()
    try:
        Bookmark, Tag, db = _models()
        rows = [(t.name, len(t.bookmarks)) for t in Tag.query.order_by(Tag.name).all()]
        if args.json:
            print(json.dumps([{"name": n, "count": c} for n, c in rows], indent=2))
        else:
            for name, count in rows:
                print("%-24s %d" % (name, count))
        print("-- %d tag(s)" % len(rows))
    finally:
        ctx.pop()
    return 0

def cmd_delete(args):
    ctx = _app()
    try:
        Bookmark, Tag, db = _models()
        bm = db.session.get(Bookmark, args.id)
        if bm is None:
            print("error: no bookmark with id %s" % args.id, file=sys.stderr)
            return 1
        title = bm.title
        db.session.delete(bm)
        db.session.commit()
        print("deleted #%s: %s" % (args.id, title))
    finally:
        ctx.pop()
    return 0

def cmd_import(args):
    from .bm.import_export import parse_netscape
    ctx = _app()
    try:
        Bookmark, Tag, db = _models()
        with open(args.file, encoding="utf-8", errors="ignore") as fh:
            parsed = parse_netscape(fh.read())
        added = 0
        for item in parsed:
            if Bookmark.query.filter_by(url=item["url"]).first():
                continue
            bm = Bookmark(url=item["url"], title=item.get("title") or item["url"])
            for name in item.get("tags") or []:
                bm.tags.append(_tag(Tag, name.strip()))
            db.session.add(bm)
            added += 1
        db.session.commit()
        print("imported %d of %d bookmark(s)" % (added, len(parsed)))
    finally:
        ctx.pop()
    return 0

def cmd_export(args):
    from .bm.import_export import export_netscape
    ctx = _app()
    try:
        Bookmark, Tag, db = _models()
        rows = [{"url": b.url, "title": b.title, "tags": [t.name for t in b.tags]}
                for b in Bookmark.query.order_by(Bookmark.id).all()]
        html = export_netscape(rows)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as fh:
                fh.write(html)
            print("wrote %d bookmark(s) to %s" % (len(rows), args.out))
        else:
            print(html)
    finally:
        ctx.pop()
    return 0

def cmd_serve(args):
    try:
        from ._app import app
    except ModuleNotFoundError as exc:
        print("error: cannot import the application (%s)" % exc, file=sys.stderr)
        return 2
    app.run(host=args.host, port=args.port, debug=args.debug)
    return 0

def build_parser():
    p = argparse.ArgumentParser(prog="bm", description="Bookmarks service CLI")
    sub = p.add_subparsers(dest="cmd", metavar="command")

    s = sub.add_parser("list", help="list bookmarks")
    s.add_argument("--tag", help="only bookmarks carrying this tag")
    s.add_argument("--limit", type=int, default=50, help="max rows (default 50)")
    s.add_argument("--json", action="store_true", help="emit JSON")
    s.set_defaults(func=cmd_list)

    s = sub.add_parser("add", help="save a URL and fetch its metadata")
    s.add_argument("url", help="http(s) URL to save")
    s.add_argument("--tags", nargs="+", default=[], help="tags to attach")
    s.set_defaults(func=cmd_add)

    s = sub.add_parser("search", help="full-text search over saved bookmarks")
    s.add_argument("query", help="FTS5 query string")
    s.add_argument("--tag", help="restrict to a tag")
    s.add_argument("--limit", type=int, default=50, help="max hits (default 50)")
    s.add_argument("--json", action="store_true", help="emit JSON")
    s.add_argument("--quiet", action="store_true",
                   help="exit 0 even when nothing matches (by default no hits is exit 1)")
    s.set_defaults(func=cmd_search)

    s = sub.add_parser("tags", help="list tags with bookmark counts")
    s.add_argument("--json", action="store_true", help="emit JSON")
    s.set_defaults(func=cmd_tags)

    s = sub.add_parser("delete", help="delete a bookmark by id")
    s.add_argument("id", type=int, help="bookmark id")
    s.set_defaults(func=cmd_delete)

    s = sub.add_parser("import", help="import a Netscape bookmarks.html file")
    s.add_argument("file", help="path to bookmarks.html")
    s.set_defaults(func=cmd_import)

    s = sub.add_parser("export", help="export bookmarks as Netscape HTML")
    s.add_argument("--out", help="write to this file instead of stdout")
    s.set_defaults(func=cmd_export)

    s = sub.add_parser("serve", help="run the development server")
    s.add_argument("--host", default="127.0.0.1")
    s.add_argument("--port", type=int, default=5000)
    s.add_argument("--debug", action="store_true")
    s.set_defaults(func=cmd_serve)
    return p

def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "func", None):
        parser.print_help()
        return 0
    return args.func(args)
