-- 🔖 bookmarks schema
CREATE TABLE bookmarks(id INTEGER PRIMARY KEY, url TEXT UNIQUE, title TEXT, description TEXT, favicon TEXT, snapshot TEXT, notes TEXT, created_at DATETIME);
CREATE TABLE tags(id INTEGER PRIMARY KEY, name TEXT UNIQUE);
CREATE TABLE bookmark_tags(bookmark_id INTEGER REFERENCES bookmarks(id), tag_id INTEGER REFERENCES tags(id), PRIMARY KEY(bookmark_id, tag_id));
