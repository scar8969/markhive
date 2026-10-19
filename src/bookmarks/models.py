from flask_sqlalchemy import SQLAlchemy

from .clock import utcnow

db = SQLAlchemy()

bookmark_tags = db.Table(
    "bookmark_tags",
    db.Column("bookmark_id", db.Integer, db.ForeignKey("bookmarks.id"), primary_key=True),
    db.Column("tag_id", db.Integer, db.ForeignKey("tags.id"), primary_key=True),
)


class Bookmark(db.Model):
    __tablename__ = "bookmarks"
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1024), unique=True)
    title = db.Column(db.String(512), default="")
    description = db.Column(db.Text, default="")
    favicon = db.Column(db.String(512), default="")
    snapshot = db.Column(db.Text, default="")
    notes = db.Column(db.Text, default="")
    created_at = db.Column(db.DateTime, default=utcnow)
    tags = db.relationship("Tag", secondary=bookmark_tags, backref="bookmarks")


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
