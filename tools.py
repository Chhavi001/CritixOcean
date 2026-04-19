from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from rich import print
from pathlib import Path
from typing import Dict, List

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

#we have to first load tavilyclient with the api key to get the agent's response
tavily_api_key = os.getenv("TAVILY_API_KEY", "").strip()
if not tavily_api_key:
    raise RuntimeError(
        "Missing required environment variable: TAVILY_API_KEY. "
        "Add it to your .env file and rerun the script."
    )
tavily=TavilyClient(api_key=tavily_api_key)


def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """Run Tavily search and return normalized result objects."""
    raw = tavily.search(query=query, max_results=max_results)
    items: List[Dict[str, str]] = []
    for r in raw.get("results", []):
        items.append(
            {
                "title": (r.get("title") or "").strip(),
                "url": (r.get("url") or "").strip(),
                "snippet": (r.get("content") or "").strip(),
            }
        )
    return items


def format_search_results(results: List[Dict[str, str]]) -> str:
    """Format normalized search results into readable text for prompts."""
    out = []
    for r in results:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['snippet'][:300]}\n"
        )
    return "\n ---- \n".join(out)


def scrape_url_content(url: str, timeout: int = 12, max_chars: int = 3000) -> str:
    """Fetch and clean visible text from a URL."""
    resp = requests.get(url, timeout=timeout, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()
    # Prefer paragraph-heavy text to reduce navigation/header noise.
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    paragraph_text = " ".join(x for x in paragraphs if len(x) > 40)
    cleaned = paragraph_text if len(paragraph_text) > 400 else soup.get_text(separator=" ", strip=True)
    return cleaned[:max_chars]


def scrape_urls(urls: List[str], max_urls: int = 4, max_chars_each: int = 2500) -> List[Dict[str, str]]:
    """Scrape a small set of URLs and return status per URL."""
    records: List[Dict[str, str]] = []
    for url in urls[:max_urls]:
        try:
            text = scrape_url_content(url, max_chars=max_chars_each)
            records.append({"url": url, "status": "ok", "content": text})
        except Exception as exc:
            records.append({"url": url, "status": "error", "error": str(exc)})
    return records

@tool 
def web_search(query: str) -> str:
    """Search the web for the given query and return titles,URLs and snippets of the top results."""
    results = search_web(query=query, max_results=5)
    return format_search_results(results)


@tool
def scrape_url(url:str)->str:
    """Scrape the content of the given URL and return the text."""
    try:
        return scrape_url_content(url=url, timeout=12, max_chars=3000)
    except Exception as e:
        return f"Could not scrape the URL:{str(e)}"
