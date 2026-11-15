import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from langchain.tools import tool
from openai import OpenAI

_ASSIGNMENT_DIR = Path(__file__).resolve().parent
_SOURCE_DIR = _ASSIGNMENT_DIR.parent
_DATABASE_PATH = _ASSIGNMENT_DIR / "chroma_data"
_COLLECTION_NAME = "blue_cross_document"
_EMBEDDING_MODEL = "text-embedding-3-small"
_GATEWAY_URL = "https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1"

load_dotenv(_SOURCE_DIR / ".env")
load_dotenv(_SOURCE_DIR / ".secrets")

_USE_GATEWAY = os.getenv("USE_GATEWAY", "FALSE").upper() == "TRUE"
_chroma_client = chromadb.PersistentClient(path=str(_DATABASE_PATH))


def _get_openai_client() -> OpenAI:
    if _USE_GATEWAY:
        gateway_key = os.getenv("API_GATEWAY_KEY")
        if not gateway_key:
            raise ValueError("Missing API_GATEWAY_KEY environment variable")
        return OpenAI(
            base_url=_GATEWAY_URL,
            api_key=os.getenv("OPENAI_API_KEY") or "any value",
            default_headers={"x-api-key": gateway_key},
        )

    return OpenAI()


def get_relevant_context(query: str, top_n: int = 3) -> str:
    """Return the most relevant passages from the assignment document."""
    if top_n < 1:
        raise ValueError("top_n must be at least 1")
    if not query.strip():
        return ""

    collection = _chroma_client.get_collection(name=_COLLECTION_NAME)
    result_count = min(top_n, collection.count())
    if result_count == 0:
        return ""

    embedding_response = _get_openai_client().embeddings.create(
        input=query,
        model=_EMBEDDING_MODEL,
    )
    query_embedding = embedding_response.data[0].embedding

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=result_count,
        include=["documents", "metadatas"],
    )
    documents = results["documents"][0] or []
    metadatas = results["metadatas"][0] or []

    passages = []
    for index, document in enumerate(documents):
        if not document:
            continue
        metadata = metadatas[index] if index < len(metadatas) else None
        source = metadata.get("source", "assignment document") if metadata else "assignment document"
        passages.append(f"Source: {source}\n{document}")
    return "\n\n---\n\n".join(passages)


@tool
def search_blue_cross(query: str) -> str:
    """Search the indexed text of The Blue Cross for passages relevant to a question."""
    return get_relevant_context(query)
