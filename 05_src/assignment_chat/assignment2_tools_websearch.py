import os

from dotenv import load_dotenv
from langchain.tools import tool
from openai import BadRequestError, OpenAI

load_dotenv(".env")
load_dotenv(".secrets")

MODEL_NAME = os.getenv("MODEL", "gpt-4o-mini")

def get_openai_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is required for hosted web search. "
            "The configured API gateway cannot be used for this tool."
        )
    return OpenAI(api_key=api_key)


@tool
def web_search(query: str) -> str:
    """Search the web for current information using the OpenAI web_search tool and return a concise answer."""
    if not query or not query.strip():
        return "Please provide a search query."

    client = get_openai_client()

    try:
        response = client.responses.create(
            model=MODEL_NAME,
            instructions=(
                "Search the live web for the requested information. Answer concisely, "
                "prioritize recent and authoritative sources, and include source links."
            ),
            input=query,
            tools=[{"type": "web_search", "search_context_size": "medium"}],
            tool_choice="required",
        )
    except BadRequestError as exc:
        message = str(exc)
        if "web_search" in message and "disabled" in message.lower():
            return (
                "Web search is unavailable in this OpenAI organization. "
                "Please enable the hosted web-search tool in your OpenAI account settings"
            )
        raise

    answer = response.output_text.strip()
    return answer or "The web search completed but returned no answer text."
