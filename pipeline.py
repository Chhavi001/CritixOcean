import random
import time
from urllib.parse import urlparse

from agents import writer_chain,critic_chain
from tools import format_search_results, scrape_urls, search_web


PREFERRED_DOMAINS = (
  "unesco.org",
  "britannica.com",
  "wikipedia.org",
  "nationalgeographic.com",
)


def _is_transient_network_error(exc: Exception) -> bool:
  """Detect common transient network errors that are safe to retry."""
  message = str(exc).lower()
  transient_markers = [
    "winerror 10053",
    "readerror",
    "timeout",
    "temporarily unavailable",
    "connection aborted",
    "connection reset",
    "network is unreachable",
    "remote protocol error",
  ]
  return any(marker in message for marker in transient_markers)


def _invoke_with_retry(step_name: str, invoke_fn, *args, max_attempts: int = 4, **kwargs):
  """Invoke an agent/chain with exponential backoff for transient failures."""
  last_exc = None
  for attempt in range(1, max_attempts + 1):
    try:
      return invoke_fn(*args, **kwargs)
    except Exception as exc:
      last_exc = exc
      if (not _is_transient_network_error(exc)) or attempt == max_attempts:
        raise
      delay = (2 ** (attempt - 1)) + random.uniform(0, 0.4)
      print(
        f"Transient network error during {step_name} "
        f"(attempt {attempt}/{max_attempts}): {exc}"
      )
      print(f"Retrying in {delay:.1f}s...")
      time.sleep(delay)

  raise RuntimeError(f"{step_name} failed after {max_attempts} attempts: {last_exc}")


def _enforce_sources(report_text: str, used_urls: list[str]) -> str:
  """Replace the Sources section with URLs that were actually scraped."""
  marker = "Sources:"
  idx = report_text.find(marker)
  if idx == -1:
    return report_text.rstrip() + "\n\nSources:\n" + "\n".join(f"* {u}" for u in used_urls)
  prefix = report_text[:idx + len(marker)]
  fixed_sources = "\n" + "\n".join(f"* {u}" for u in used_urls)
  return prefix + fixed_sources


def _notify(progress_callback, stage: str, message: str, payload: dict | None = None) -> None:
  """Send progress updates to the UI when a callback is supplied."""
  if progress_callback:
    progress_callback(stage, message, payload or {})


def run_research_pipeline(
  topic: str,
  progress_callback=None,
  max_search_results: int = 5,
  max_scrape_urls: int = 4,
  max_chars_each: int = 2500,
) -> dict:
  state={}
  try:
    #search agent working
    print("\n" + "=" * 50)
    print("step1-search agent is working ...")
    print("=" * 50)
    _notify(progress_callback, "search", "Searching the web for reliable sources...", {"topic": topic})

    search_items = _invoke_with_retry(
      "search step",
      search_web,
      f"recent, reliable and detailed information about: {topic}",
      max_results=max_search_results,
    )
    if not search_items:
      raise RuntimeError("Search returned no results.")

    source_urls = [item["url"] for item in search_items if item.get("url")]
    prioritized = sorted(
      source_urls,
      key=lambda url: (0 if any(d in (urlparse(url).netloc or "") for d in PREFERRED_DOMAINS) else 1),
    )
    state["source_urls"] = prioritized
    state["search_items"] = search_items
    state["search_results"] = format_search_results(search_items)
    print("\n search result ",state["search_results"])
    _notify(
      progress_callback,
      "search",
      f"Found {len(search_items)} candidate sources.",
      {"source_urls": state["source_urls"], "search_results": state["search_results"]},
    )

    #step2-reader agent working
    print("\n" + "=" * 50)
    print("step2-reader agent is working ...")
    print("=" * 50)
    _notify(progress_callback, "scrape", "Scraping and cleaning the top source pages...", {"source_urls": state["source_urls"]})
    scrape_records = _invoke_with_retry(
      "reader step",
      scrape_urls,
      state["source_urls"],
      max_urls=max_scrape_urls,
      max_chars_each=max_chars_each,
    )
    successful = [r for r in scrape_records if r.get("status") == "ok" and r.get("content")]
    failed = [r for r in scrape_records if r.get("status") != "ok"]

    if not successful:
      raise RuntimeError(
        "Reader step could not scrape any source URLs. "
        "Please check network/firewall settings or try another topic."
      )

    chunks = []
    for rec in successful:
      chunks.append(f"URL: {rec['url']}\nContent: {rec['content']}")
    state["scraped_content"] = "\n\n---\n\n".join(chunks)
    state["used_source_urls"] = [rec["url"] for rec in successful]
    state["scrape_records"] = scrape_records
    state["scrape_diagnostics"] = {
      "attempted": len(scrape_records),
      "succeeded": len(successful),
      "failed": len(failed),
      "failed_urls": [r.get("url", "") for r in failed],
    }
    print("\n scraped content ",state["scraped_content"])
    print("\n scrape diagnostics ", state["scrape_diagnostics"])
    _notify(
      progress_callback,
      "scrape",
      f"Scraped {len(successful)} pages successfully.",
      {"scrape_diagnostics": state["scrape_diagnostics"]},
    )

    #step 3-writer agent working
    print("\n" + "=" * 50)
    print("step3-writer agent is working ...")
    print("=" * 50)
    _notify(progress_callback, "write", "Drafting the research brief...", {})

    state["report"] = _invoke_with_retry("writer step", writer_chain.invoke, {
      "topic":topic,
      "source_urls":"\n".join(state["used_source_urls"]),
      "search_results":state["search_results"],
      "scraped_content":state["scraped_content"]
    })

    state["report"] = _enforce_sources(state["report"], state["used_source_urls"])
    print("\n Final report\n",state["report"])
    _notify(progress_callback, "write", "Draft completed and sources verified.", {"report": state["report"]})

    #critic report
    print("\n" + "=" * 50)
    print("step4-critic agent is working ...")
    print("=" * 50)
    _notify(progress_callback, "critic", "Reviewing the draft for quality and grounding...", {})
    state["feedback"] = _invoke_with_retry("critic step", critic_chain.invoke, {
      "topic": topic,
      "source_urls": "\n".join(state["used_source_urls"]),
      "search_results": state["search_results"],
      "scraped_content": state["scraped_content"],
      "draft_summary": state["report"]
    })

    print("\n critic report \n",state["feedback"])
    _notify(progress_callback, "critic", "Review complete.", {"feedback": state["feedback"]})
    return state
  except Exception as exc:
    _notify(progress_callback, "error", str(exc), {"error": str(exc)})
    if _is_transient_network_error(exc):
      raise RuntimeError(
        "Pipeline failed due to a transient network disconnection while calling the model API. "
        "Please check VPN/firewall/proxy settings and rerun. "
        f"Original error: {exc}"
      ) from exc
    raise RuntimeError(f"Pipeline failed: {exc}") from exc



if __name__=="__main__":
  topic=input("\n Enter a research topic: ")
  run_research_pipeline(topic)