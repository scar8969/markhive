from .fetch import fetch_meta
from .search import search
from ..models import Bookmark, Tag, db

from flask import Blueprint, jsonify, request

bp = Blueprint("bm", __name__)

@bp.post("/api/bookmarks")
def add_bookmark():
    d = request.get_json(force=True, silent=True) or {}
    url = d.get("url", "")
    if not url:
        return jsonify({"error": "url required"}), 400
    if Bookmark.query.filter_by(url=url).first():
        return jsonify({"error": "duplicate"}), 409
    meta = fetch_meta(url)
    bm = Bookmark(url=url, title=meta.get("title", url),
                  description=meta.get("description", ""), favicon=meta.get("favicon", ""),
                  snapshot=meta.get("snapshot", ""), notes=d.get("notes", ""))
    raw = d.get("tags", [])
    if isinstance(raw, str):
        raw = raw.split(",")
    seen = set()
    with db.session.no_autoflush:
        for tname in raw:
            name = str(tname).strip()
            if not name or name in seen:
                continue
            seen.add(name)
            tag = Tag.query.filter_by(name=name).first()
            if tag is None:
                tag = Tag(name=name)
                db.session.add(tag)
            bm.tags.append(tag)
    db.session.add(bm)
    db.session.commit()
    return jsonify({"id": bm.id, "title": bm.title})

@bp.get("/api/bookmarks")
def list_bookmarks():
    q = request.args.get("q", "")
    tag = request.args.get("tag", "")
    query = Bookmark.query
    if q:
        ids = [b["id"] for b in search(q)]
        query = query.filter(Bookmark.id.in_(ids))
    if tag:
        query = query.filter(Bookmark.tags.any(Tag.name == tag))
    rows = [{"id": b.id, "title": b.title, "url": b.url,
             "tags": [t.name for t in b.tags], "created_at": b.created_at.isoformat() if b.created_at else ""}
            for b in query.order_by(Bookmark.id.desc()).limit(100).all()]
    return jsonify({"bookmarks": rows})

@bp.delete("/api/bookmarks/<int:bid>")
def delete(bid):
    b = Bookmark.query.get_or_404(bid)
    db.session.delete(b)
    db.session.commit()
    return jsonify({"status": "deleted"})

@bp.get("/api/tags")
def tags():
    return jsonify({"tags": [{"name": t.name, "count": len(t.bookmarks)} for t in Tag.query.all()]})
