"""Built-in web search tool."""

from __future__ import annotations

from typing import Any


async def search(input: dict[str, Any]) -> str:
    """Perform a web search using httpx."""
    import httpx

    query = input.get("query", "")
    if not query:
        return "No query provided."

    headers = {"User-Agent": "Mozilla/5.0 (compatible; GraphAgent/0.1)"}
    params = {"q": query, "kl": "us-en"}

    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(
                "https://html.duckduckgo.com/html/", params=params, headers=headers
            )
            resp.raise_for_status()
            results = _parse_ddg_html(resp.text, max_results=input.get("num_results", 5))
            return "\n\n".join(results) or "No results found."
    except Exception as exc:
        return f"Search error: {exc}"


def _parse_ddg_html(html: str, max_results: int = 5) -> list[str]:
    """Minimal regex-based parser for DuckDuckGo Lite results."""
    import re

    titles = re.findall(r'class="result__title"[^>]*>.*?<a[^>]+>([^<]+)<', html, re.S)
    snippets = re.findall(r'class="result__snippet"[^>]*>([^<]+)<', html, re.S)
    out = []
    for i, (title, snippet) in enumerate(zip(titles, snippets)):
        if i >= max_results:
            break
        out.append(f"**{title.strip()}**\n{snippet.strip()}")
    return out
