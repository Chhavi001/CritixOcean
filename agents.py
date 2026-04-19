from langchain.agents import create_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


def _get_required_env(var_name: str) -> str:
  """Return a required env var or raise a clear startup error."""
  value = os.getenv(var_name, "").strip()
  if not value:
    raise RuntimeError(
      f"Missing required environment variable: {var_name}. "
      "Add it to your .env file and rerun the script."
    )
  return value


def _get_google_api_key() -> str:
  """Load a Google AI Studio API key from the preferred env var names."""
  key = os.getenv("GOOGLE_API_KEY", "").strip()
  if not key:
    key = os.getenv("OPENAI_API_KEY", "").strip()
  if not key:
    raise RuntimeError(
      "Missing required environment variable: GOOGLE_API_KEY. "
      "Set GOOGLE_API_KEY in your .env file using a Google AI Studio key."
    )
  return key


google_api_key = _get_google_api_key()
gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()

#model setup
llm=ChatGoogleGenerativeAI(
  model=gemini_model,
  temperature=0,
  google_api_key=google_api_key,
)

#first agent
def build_search_agent():
  return  create_agent(
    model=llm,
    tools=[web_search]
  )

#second agent,the reader agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url]
    )

#writer chain
writer_prompt=ChatPromptTemplate.from_messages([
  (
    "system",
    """You are an expert news writer.

Your goal is to convert raw search results and scraped text into a clean, factual, point-based news brief.

Follow these rules strictly:
1. Use only the provided data. Do not invent facts.
2. Focus on latest and most relevant updates.
3. Remove duplicate or repetitive points.
4. Keep language simple, clear, and professional.
5. If sources conflict, mention uncertainty briefly.
6. If data is insufficient, clearly say what is missing.

Output format:
- Headline: one clear line
- Key Updates: 5 to 8 bullet points
- Why It Matters: 2 to 3 bullet points
- Sources: bullet list of URLs used

Style guide:
- Short sentences
- No hype or sensational tone
- No personal opinions
- No markdown tables
- Keep total response under 220 words"""
  ),
  (
    "human",
    """Create a point-based news summary.

Topic:
{topic}

Source URLs:
{source_urls}

Search Results:
{search_results}

Scraped Content:
{scraped_content}"""
  )
])

writer_chain=writer_prompt| llm | StrOutputParser()

#critic_chain
# this is for the critic agent to evaluate the output of the writer chain and provide feedback for improvement

critic_prompt=ChatPromptTemplate.from_messages([
  (
    "system",
    """You are a strict and constructive news editor.

Your job is to review a draft news summary and return precise, actionable feedback.

Evaluation checklist:
1. Factual Accuracy: no unsupported claims, no hallucinations.
2. Relevance: covers the most important and recent developments.
3. Structure: follows required format (Headline, Key Updates, Why It Matters, Sources).
4. Clarity: concise, readable, no vague phrasing.
5. Source Grounding: claims are traceable to provided search/scraped content.
6. Duplicates/Noise: remove repetition and low-value lines.
7. Tone: neutral, professional, non-sensational.

Scoring:
- Give a score out of 10.
- Deduct points with short reasons.

Output format:
- Verdict: PASS or REVISE
- Score: X/10
- Strengths: 3 bullet points
- Issues: up to 6 bullet points (severity: high/medium/low)
- Missing Information: bullet points
- Suggested Rewrite Plan: 5 clear steps

Rules:
- Be specific and quote problematic lines when possible.
- If output is good, still provide small improvements.
- Keep feedback under 220 words."""
  ),
  (
    "human",
    """Review the draft summary and provide editorial feedback.

Topic:
{topic}

Source URLs:
{source_urls}

Search Results:
{search_results}

Scraped Content:
{scraped_content}

Draft Summary:
{draft_summary}"""
  )
])

critic_chain=critic_prompt | llm | StrOutputParser()