import os

from .bm.api import bp
from .bm.fetch import fetch_meta
from .bm.import_export import export_netscape
from .bm.search import search as bm_search
from .models import Bookmark, Tag, db

from flask import Flask, Response, flash, jsonify, redirect, render_template, request, url_for
from . import paths

# templates/ is copied to the project root by the build, next to web/.

def build_app():
    """Build the application: configuration, database, then routes."""
    app = Flask(__name__, template_folder=str(paths.TEMPLATES_DIR))
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("BOOKMARKS_DB_URI", "sqlite:///" + str(paths.INSTANCE_DIR / "bookmarks.db"))
    app.config["SECRET_KEY"] = os.environ.get("BOOKMARKS_SECRET_KEY", "bookmarks-local")
    db.init_app(app)
    with app.app_context():
        db.create_all()
    app.register_blueprint(bp)

    @app.context_processor
    def _inject():
        return {"app_name": "🔖 bookmarks", "stats": _stats(), "all_tags": _all_tags()}

    def _stats():
        return {"bookmarks": Bookmark.query.count(), "tags": Tag.query.count()}

    def _all_tags():
        return [{"name": t.name, "count": len(t.bookmarks)} for t in Tag.query.order_by(Tag.name).all()]

    @app.get("/")
    def index():
        q = (request.args.get("q") or "").strip()
        tag = (request.args.get("tag") or "").strip()
        if q:
            ids = [row["id"] for row in bm_search(q)]
            query = Bookmark.query.filter(Bookmark.id.in_(ids)) if ids else Bookmark.query.filter(db.false())
        else:
            query = Bookmark.query
        if tag:
            query = query.filter(Bookmark.tags.any(Tag.name == tag))
        bookmarks = query.order_by(Bookmark.id.desc()).limit(200).all()
        return render_template("index.html", bookmarks=bookmarks, q=q, tag=tag)

    @app.post("/bookmarks/add")
    def add():
        url = (request.form.get("url") or "").strip()
        notes = (request.form.get("notes") or "").strip()
        raw_tags = request.form.get("tags", "")
        if not url:
            flash("A URL is required.", "error")
            return redirect(url_for("index"))
        if Bookmark.query.filter_by(url=url).first():
            flash("Already saved: %s" % url, "error")
            return redirect(url_for("index"))
        meta = fetch_meta(url)
        bm = Bookmark(url=url, title=meta.get("title") or url, description=meta.get("description", ""),
                      favicon=meta.get("favicon", ""), snapshot=meta.get("snapshot", ""), notes=notes)
        names = [n.strip() for n in raw_tags.split(",") if n.strip()]
        seen = set()
        with db.session.no_autoflush:
            for name in names:
                if name in seen:
                    continue
                seen.add(name)
                tag = Tag.query.filter_by(name=name).first()
                if tag is None:
                    tag = Tag(name=name)
                    db.session.add(tag)
                bm.tags.append(tag)
        db.session.add(bm)
        db.session.commit()
        flash("Saved %s%s." % (bm.title, (" [%s]" % ", ".join(names)) if names else ""), "success")
        return redirect(url_for("index"))

    @app.post("/bookmarks/<int:bid>/delete")
    def delete(bid):
        bm = db.session.get(Bookmark, bid)
        if bm is None:
            flash("No bookmark with id %s." % bid, "error")
        else:
            title = bm.title or bm.url
            db.session.delete(bm)
            db.session.commit()
            flash("Deleted %s." % title, "success")
        return redirect(url_for("index"))

    @app.get("/export.html")
    def export():
        rows = [{"url": b.url, "title": b.title or b.url, "tags": [t.name for t in b.tags]}
                for b in Bookmark.query.order_by(Bookmark.id).all()]
        return Response(export_netscape(rows), mimetype="text/html",
                        headers={"Content-Disposition": "attachment; filename=bookmarks.html"})

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "bookmarks": Bookmark.query.count(), "tags": Tag.query.count()})

    # python -m web.app
    if __name__ == "__main__":
        app.run(host="127.0.0.1", port=5000, debug=False)

    return app

app = build_app()
