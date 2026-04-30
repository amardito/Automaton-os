from ddgs import DDGS


def web_search(query: str, max_results: int = 5) -> list[dict]:
    results: list[dict] = []

    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=max_results):
            results.append(
                {
                    "title": item.get("title", ""),
                    "url": item.get("href", ""),
                    "snippet": item.get("body", ""),
                }
            )

    return results