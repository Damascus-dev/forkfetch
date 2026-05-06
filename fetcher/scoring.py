from __future__ import annotations

import math
from datetime import datetime, timezone

from fetcher.utils import parse_github_datetime


def score_repository(repo: dict, query: str) -> float:
    stars = int(repo.get("stargazers_count") or 0)
    archived = bool(repo.get("archived"))
    open_issues = int(repo.get("open_issues_count") or 0)

    score = math.log(stars + 1)
    score += freshness_bonus(repo.get("pushed_at"))
    score += keyword_match_bonus(repo, query)

    if archived:
        score -= 3.0

    if stars > 0:
        issue_ratio = open_issues / stars
        if issue_ratio < 0.05:
            score += 0.3
        elif issue_ratio > 0.5:
            score -= 0.6

    if repo.get("description"):
        score += 0.15

    if repo.get("default_branch"):
        score += 0.1

    return round(score, 2)


def freshness_bonus(pushed_at: str | None) -> float:
    pushed = parse_github_datetime(pushed_at)
    if pushed is None:
        return 0.0

    age_days = max((datetime.now(timezone.utc) - pushed).days, 0)
    if age_days <= 7:
        return 2.2
    if age_days <= 30:
        return 1.6
    if age_days <= 90:
        return 1.0
    if age_days <= 180:
        return 0.4
    if age_days <= 365:
        return 0.0
    return -0.8


def keyword_match_bonus(repo: dict, query: str) -> float:
    terms = [term.lower() for term in query.split() if term.strip()]
    if not terms:
        return 0.0

    haystacks = [
        str(repo.get("name") or "").lower(),
        str(repo.get("full_name") or "").lower(),
        str(repo.get("description") or "").lower(),
        " ".join(topic.lower() for topic in repo.get("topics", [])),
    ]
    joined = " ".join(haystacks)
    matches = sum(1 for term in terms if term in joined)
    return min(matches * 0.35, 1.75)
