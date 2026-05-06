from __future__ import annotations

from dataclasses import dataclass

import httpx


GITHUB_API_BASE = "https://api.github.com"


class GitHubApiError(RuntimeError):
    """Raised when the GitHub API returns an error response."""


@dataclass(slots=True)
class SearchResponse:
    query: str
    total_count: int
    items: list[dict]


class GitHubClient:
    def __init__(self, token: str | None = None, timeout: float = 20.0) -> None:
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "fetcher-cli",
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.AsyncClient(
            base_url=GITHUB_API_BASE,
            headers=headers,
            timeout=timeout,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def search_repositories(self, query: str, per_page: int = 10) -> SearchResponse:
        response = await self._client.get(
            "/search/repositories",
            params={
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": per_page,
            },
        )
        self._raise_for_error(response)
        payload = response.json()
        return SearchResponse(
            query=query,
            total_count=payload.get("total_count", 0),
            items=payload.get("items", []),
        )

    async def get_repository(self, full_name: str) -> dict:
        response = await self._client.get(f"/repos/{full_name}")
        self._raise_for_error(response)
        return response.json()

    @staticmethod
    def _raise_for_error(response: httpx.Response) -> None:
        if response.status_code < 400:
            return
        message = response.text
        if response.headers.get("content-type", "").startswith("application/json"):
            payload = response.json()
            message = payload.get("message", message)
        raise GitHubApiError(f"GitHub API error ({response.status_code}): {message}")
