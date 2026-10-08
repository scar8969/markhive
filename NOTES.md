== curl ==
# POST /api/bookmarks  {"url":"https://arxiv.org/abs/2401.00000","tags":["ai","dev"],"notes":"…"}
# GET  /api/bookmarks?q=llm&tag=ai
# DELETE /api/bookmarks/1
# GET  /api/tags
# CLI: bm add https://arxiv.org/abs/2401.00000 --tags ai dev

== session plan ==
# Session 1: fetch (meta) + models → tests
# Session 2: api + search FTS5 + tags → tests
# Session 3: import/export + web + cli → screenshots → README → CI/Docker/Pages → tag
