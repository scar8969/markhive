def search(q, tag="", limit=50):
    from ..models import Bookmark, Tag, db

    q = (q or "").strip()
    ids = []
    if q:
        # FTS5 index is optional: create it if the SQLite build supports it, then query it.
        try:
            db.session.execute(
                db.text(
                    "CREATE VIRTUAL TABLE IF NOT EXISTS bm_fts USING fts5(title, description, notes)"
                )
            )
            db.session.commit()
        except Exception:
            db.session.rollback()
        try:
            rows = db.session.execute(
                db.text("SELECT rowid FROM bm_fts WHERE bm_fts MATCH :q LIMIT :lim"),
                {"q": q, "lim": limit},
            ).fetchall()
            ids = [r[0] for r in rows]
        except Exception:
            db.session.rollback()
            ids = []
        if not ids:
            # The index is empty or the query is not valid FTS5 syntax, so scan the rows directly.
            like = "%" + q.replace("%", "").replace("_", "") + "%"
            ids = [
                b.id
                for b in Bookmark.query.filter(
                    db.or_(
                        Bookmark.title.ilike(like),
                        Bookmark.description.ilike(like),
                        Bookmark.notes.ilike(like),
                    )
                )
                .limit(limit)
                .all()
            ]
    query = Bookmark.query
    if q:
        query = query.filter(Bookmark.id.in_(ids)) if ids else query.filter(db.false())
    if tag:
        query = query.filter(Bookmark.tags.any(Tag.name == tag))
    return [
        {"id": b.id, "title": b.title, "url": b.url, "tags": [t.name for t in b.tags]}
        for b in query.limit(limit).all()
    ]
