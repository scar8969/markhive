<p align="center">
  <img src="docs/assets/screens/root.png" alt="markhive running" width="900">
</p>

<h1 align="center">markhive</h1>

<p align="center"><b>Save a URL once, keep the metadata, tag it, search it.</b></p>

<p align="center">
  <a href="https://github.com/scar8969/markhive/actions/workflows/ci.yml"><img src="https://github.com/scar8969/markhive/actions/workflows/ci.yml/badge.svg" alt="ci"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/tests-23%20passed-2ea44f" alt="tests: 23 passed"></a> <a href="#quality-gates"><img src="https://img.shields.io/badge/coverage-51.2%-yellow" alt="coverage: 51.2%"></a> <a href="#api"><img src="https://img.shields.io/badge/routes-10%20live-0969da" alt="routes: 10 live"></a> <a href="#requirements"><img src="https://img.shields.io/badge/python-3.11%2B-3776ab" alt="python: 3.11+"></a> <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-2ea44f" alt="license: MIT"></a>
</p>

markhive fetches a saved URL once, stores the title, description and favicon, and lets you tag and search the collection. Import and export cover the usual formats.

---

**Contents** &nbsp;·&nbsp; [Why](#why-this-exists) &nbsp;·&nbsp; [What it does](#what-it-does) &nbsp;·&nbsp; [Quickstart](#quickstart) &nbsp;·&nbsp; [Screenshots](#screenshots) &nbsp;·&nbsp; [API](#api) &nbsp;·&nbsp; [CLI](#cli) &nbsp;·&nbsp; [Configuration](#configuration) &nbsp;·&nbsp; [Measured](#measured-not-estimated) &nbsp;·&nbsp; [How a request flows](#how-a-request-flows) &nbsp;·&nbsp; [Architecture](#architecture) &nbsp;·&nbsp; [Quality gates](#quality-gates) &nbsp;·&nbsp; [Development](#development) &nbsp;·&nbsp; [Deploy](#deploy) &nbsp;·&nbsp; [Limits](#limits-stated-rather-than-hidden)

## Why this exists

Browser bookmarks are write-only. Fetching metadata at save time — and storing it — means search works on what the page said, not just on the URL you typed.

## What it does

| Capability | How it works |
| --- | --- |
| **Metadata capture** | Title, description and favicon are read once at save time and stored with the bookmark. |
| **Tags** | Many-to-many tags with a tag list endpoint for the filter UI. |
| **Search** | Matches across title, description and URL. |
| **Import and export** | Netscape bookmark HTML in and out, plus a CLI for both. |

## Quickstart

```sh
git clone https://github.com/scar8969/markhive.git
cd markhive
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python wsgi.py                                 # http://127.0.0.1:8000
```

It is up when this answers:

```sh
curl -s http://127.0.0.1:8000/api/bookmarks
```

## Screenshots

Captured from the running service with headless Chromium at 1440×900, one image per page, committed under [`docs/assets/screens/`](docs/assets/screens/).

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/healthz.png" alt="/healthz" width="100%"><br><sub><code>/healthz</code> &middot; 8.3 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/livez.png" alt="/livez" width="100%"><br><sub><code>/livez</code> &middot; 7.3 KB</sub></td>
</tr>
</table>

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/metrics.png" alt="/metrics" width="100%"><br><sub><code>/metrics</code> &middot; 14.9 KB</sub></td>
<td width="50%"><img src="docs/assets/screens/readyz.png" alt="/readyz" width="100%"><br><sub><code>/readyz</code> &middot; 7.7 KB</sub></td>
</tr>
</table>

<table>
<tr>
<td width="50%"><img src="docs/assets/screens/version.png" alt="/version" width="100%"><br><sub><code>/version</code> &middot; 25.7 KB</sub></td>
</tr>
</table>

## API

Every route below is declared in [`openapi/markhive.yaml`](openapi/markhive.yaml) and exercised by the live probe recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Method | Path | What it does |
| --- | --- | --- |
| `GET` | `/api/bookmarks` | list+search |
| `POST` | `/api/bookmarks` | add |
| `DELETE` | `/api/bookmarks/<id>` | delete |
| `GET` | `/api/tags` | tags |

## CLI

The same operations without an HTTP client. Installed as `markhive`, and runnable from a checkout with no install:

```sh
python -m bookmarks.cli --help
```

```text
usage: bm [-h] command ...

Bookmarks service CLI

positional arguments:
  command
    list      list bookmarks
    add       save a URL and fetch its metadata
    search    full-text search over saved bookmarks
    tags      list tags with bookmark counts
    delete    delete a bookmark by id
    import    import a Netscape bookmarks.html file
    export    export bookmarks as Netscape HTML
    serve     run the development server

options:
  -h, --help  show this help message and exit
```

## Configuration

Environment only — there is no config file. Copy `.env.example` to `.env` and edit; `APP_ENV=production` refuses to start without `SECRET_KEY`.

| Variable | Default | Meaning |
| --- | --- | --- |
| `APP_ENV` | `development` | development \| staging \| production; production enforces the secret. |
| `SECRET_KEY` | `change-me-in-production` | Session/CSRF signing key. Required when APP_ENV=production. |
| `HOST` | `0.0.0.0` | Interface the dev server binds. |
| `PORT` | `8000` | Port the dev server and the container listen on. |
| `DEBUG` | `false` | Flask debug mode. Never true in production. |
| `MAX_CONTENT_LENGTH` | `8388608` | Largest accepted request body, in bytes. |
| `DATA_DIR` | `(empty)` | Where uploaded and generated files live. |
| `INSTANCE_DIR` | `(empty)` | Where the SQLite file and instance state live. |
| `LOG_DIR` | `(empty)` | Where rotated log files are written, if file logging is on. |
| `LOG_LEVEL` | `INFO` | DEBUG \| INFO \| WARNING \| ERROR. |
| `LOG_JSON` | `true` | true emits one JSON object per line; false is human-readable. |
| `REQUEST_ID_HEADER` | `X-Request-ID` | Header echoed on every response and stamped on every log line. |
| `BOOKMARKS_SECRET_KEY` | `bookmarks-local` | Flask session key; set it in production. |

## Measured, not estimated

Produced on this checkout by `pytest --cov` and by booting `wsgi.py` and issuing one real GET per documented path. The commands are recorded in [`docs/EVIDENCE.md`](docs/EVIDENCE.md).

| Signal | Value |
| --- | --- |
| Tests | **23 / 23 passed** (1.7 s, exit 0) |
| Line coverage | **51.2%** — 426 of 782 statements |
| Source | 15 files / 1,627 lines |
| Test code | 4 files / 230 lines |
| Documented paths | 3 in the spec, 2 GET |
| Live probe | 10 GET requests to the booted app, **10 answered 200** |
| Median latency | **6.2 ms** (single uncached request, dev server) |
| Slowest / fastest | 100.1 ms `/` / 4.6 ms `/version` |
| Bytes served | 7.3 KB across 10 responses |
| Screenshots | 6 captured |

## How a request flows

```text
client
  │  HTTP
  ▼
wsgi.py ──▶ bookmarks/app.py:get_app()
                │  reads config once (bookmarks/config.py)
                │  registers the `bm` blueprint
                ▼
           route handler
             ├──▶ bookmarks/models.py        tables, via Flask-SQLAlchemy
             ├──▶ bookmarks/errors.py        raises typed errors → one JSON envelope
             └──▶ bookmarks/observability.py JSON log line + X-Request-ID
```

Every response carries `X-Request-ID`, and the matching log line is written once at the end of the request with the status and duration, so a report of "it failed" is one `grep` away from the traceback.

## Architecture

```
markhive/
├── src/bookmarks/
│   ├── http.py                         379  HTTP plumbing for bookmarks: correlation ids, access
│   ├── cli.py                          273  Command line front-end for the bookmarks service
│   ├── config.py                       172  Environment-driven configuration for bookmarks
│   ├── observability.py                169  Structured logging and request correlation for bookm
│   ├── _app.py                         132  
│   ├── app.py                          119  Application factory for bookmarks
│   ├── errors.py                       108  Typed application errors and their HTTP mapping for 
│   ├── bm/api.py                        81  
│   ├── paths.py                         52  Filesystem layout for bookmarks
│   ├── bm/search.py                     50  
│   ├── models.py                        31  
│   ├── bm/fetch.py                      31  
├── openapi/markhive.yaml                  the contract of record
├── schema/markhive.sql                    the DDL
├── tests/                       the suite that has to stay green
├── docs/EVIDENCE.md             the recorded live route walk
├── Dockerfile                   multi-stage build
└── wsgi.py                      entry point
```

The package keeps one shape across the service: `config.py` reads the environment once, `observability.py` emits structured JSON logs carrying a request id, `errors.py` turns exceptions into a single JSON envelope, `models.py` holds the tables, and the `bm/` package holds the routes.

## Quality gates

| Gate | Command | Threshold |
| --- | --- | --- |
| Suite | `pytest -q` | all green |
| Coverage | `pytest --cov` | floor in `pyproject.toml`, set below the measured value |
| Lint | `ruff check src tests` | zero findings |
| Format | `ruff format --check src tests` | zero reformats |
| Types | `mypy src` | zero errors |
| Security | `bandit -c pyproject.toml -r src` | reviewed skip list, no unreviewed finding |
| Live routes | boot `wsgi.py`, one GET per documented path | no 5xx, no undocumented guard |

CI runs the first six on Python 3.11, 3.12 and 3.13 on every push to `main`, plus a container build — [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Development

```sh
pip install -e ".[dev]"
python -m pytest -q                      # the suite
python -m pytest --cov                   # with the coverage floor
python -m ruff check src tests           # lint
python -m ruff format --check src tests  # formatting
python -m mypy src                       # types
python -m bandit -c pyproject.toml -r src  # security
pre-commit install                       # the same checks on commit
```

Dependabot opens grouped PRs for the dev tooling weekly and for actions and the base image monthly.

## Deploy

```sh
docker build -t markhive .
docker run --rm -p 8000:8000 --env-file .env.example markhive
```

A `docker-compose.yml` is included for a local run with a volume for the SQLite file. The image runs as a non-root user and serves through gunicorn.

## Limits, stated rather than hidden

- Metadata is a single fetch; a page that changes later keeps its original snapshot.
- Favicons are stored as URLs, not downloaded.

## License

MIT — see [LICENSE](LICENSE).
