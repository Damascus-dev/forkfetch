# Fetcher MVP — Smart GitHub Repo Discovery CLI

## Vision

Build a lightweight CLI tool that:
- searches GitHub repositories
- ranks them intelligently
- displays clean terminal UI
- supports direct cloning
- stores cached results locally
- becomes extensible later

---

# Core MVP Goals

The CLI should allow:

```bash
ffetch search "jwt auth node"
```

Outputs:
- repo name
- description
- stars
- language
- update activity
- calculated score

Additional commands:

```bash
ffetch clone owner/repo
ffetch top
ffetch refresh
```

---

# Tech Stack

| Component | Choice |
|---|---|
| Language | Python 3.11+ |
| CLI Framework | Typer |
| Terminal UI | Rich |
| HTTP Requests | httpx |
| Database | SQLite |
| Packaging | pyproject.toml |
| Async Support | asyncio |

---

# Recommended Libraries

Install:

```bash
pip install typer rich httpx aiosqlite
```

Optional later:
- textual
- qdrant-client
- sentence-transformers

---

# Folder Structure

```text
fetcher/
│
├── fetcher/
│   ├── __init__.py
│   ├── main.py
│   ├── github_api.py
│   ├── scoring.py
│   ├── database.py
│   ├── clone.py
│   ├── config.py
│   ├── cache.py
│   └── utils.py
│
├── data/
│   └── repos.db
│
├── README.md
├── requirements.txt
└── pyproject.toml
```

---

# MVP Features

## 1. Search GitHub Repositories

Command:

```bash
ffetch search "react auth"
```

Use:
- GitHub Search API
- optional topic/language filters

API Endpoint:

```text
https://api.github.com/search/repositories?q=
```

---

## 2. Intelligent Ranking

Simple scoring formula:

```python
score = (
    log(stars + 1)
    + freshness_bonus
    + keyword_match_bonus
)
```

Additional signals:
- recent commits
- open issues ratio
- archived status
- README existence

---

## 3. Terminal UI

Use Rich library for:
- tables
- panels
- colored output
- progress bars

Example output:

```text
┌─────────────────────────────────────┐
│ expressjs/express                  │
│ Fast web framework for Node.js     │
│ ⭐ 68k | JS | Updated: 2 days ago  │
│ Score: 9.4                         │
└─────────────────────────────────────┘
```

---

## 4. Direct Repo Cloning

Command:

```bash
ffetch clone expressjs/express
```

Implementation:
- subprocess
- git clone

Example:

```python
subprocess.run(["git", "clone", repo_url])
```

---

## 5. SQLite Caching

Database stores:
- repo metadata
- scores
- search history
- timestamps

Schema:

```sql
CREATE TABLE repos (
    id INTEGER PRIMARY KEY,
    full_name TEXT,
    description TEXT,
    stars INTEGER,
    language TEXT,
    score REAL,
    updated_at TEXT,
    fetched_at TEXT
);
```

---

# CLI Commands

## Search

```bash
ffetch search "jwt auth"
```

## Clone

```bash
ffetch clone owner/repo
```

## Top Rated Cached Repos

```bash
ffetch top
```

## Refresh Cache

```bash
ffetch refresh
```

---

# GitHub Authentication

Use Personal Access Token.

Store config:

Linux:
```text
~/.config/fetcher/config.json
```

Windows:
```text
%APPDATA%/fetcher/config.json
```

Example:

```json
{
  "github_token": "YOUR_TOKEN"
}
```

---

# Main Modules

## main.py

Responsibilities:
- Typer CLI entrypoint
- command registration
- user interaction

---

## github_api.py

Responsibilities:
- API calls
- repo search
- repo metadata parsing
- pagination

---

## scoring.py

Responsibilities:
- ranking logic
- scoring formula
- normalization

---

## database.py

Responsibilities:
- SQLite setup
- inserts
- updates
- caching

---

## clone.py

Responsibilities:
- repo cloning
- folder management

---

# Future Features (NOT MVP)

Do NOT implement yet:
- AI embeddings
- semantic search
- web crawling
- recommendation engine
- local vector databases
- Reddit scraping
- ML ranking

Keep MVP lean.

---

# Recommended Development Timeline

## Day 1
- CLI setup
- GitHub API integration

## Day 2
- Rich terminal output
- search results rendering

## Day 3
- SQLite caching

## Day 4
- ranking system

## Day 5
- clone command
- polish and packaging

---

# Packaging

## Linux
Target:
- pipx
- AUR package

## Windows
Target:
- Scoop
- Chocolatey

---

# Recommended MVP Constraints

Avoid:
- large background indexing
- heavy AI workloads
- massive scraping

Optimize for:
- low RAM
- low CPU usage
- fast startup
- offline cache support

---

# Long-Term Vision

The long-term goal is NOT:
> another GitHub search wrapper

The real vision:
> a developer intent engine that finds the best implementation instantly

Potential future flow:

```bash
ffetch use jwt-auth
```

Which:
- searches
- ranks
- clones
- installs
- opens docs
- prepares starter environment

---

# Suggested Immediate Next Steps

1. Build CLI skeleton
2. Implement GitHub search
3. Add Rich output
4. Add scoring
5. Add SQLite cache
6. Add cloning support
7. Package for pipx

---

# Suggested Project Name Ideas

- fetcher
- repofox
- gitseek
- repohunt
- devfetch
- codexfetch
- repoquery

---

# Final Notes

Keep the MVP:
- simple
- fast
- stable
- extensible

Focus on:
- developer workflow
- quality ranking
- excellent CLI UX

Avoid premature AI complexity.
