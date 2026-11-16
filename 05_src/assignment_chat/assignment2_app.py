import logging
from typing import Any

from langchain_core.messages import HumanMessage, AIMessage
import gradio as gr
from dotenv import load_dotenv
from assignment_chat.assignment2_main import get_graph

_logs = logging.getLogger(__name__)

load_dotenv(".env")
load_dotenv(".secrets")

llm = get_graph()


def assignment_chat(message: str, history: list[dict[str, Any]]) -> str:
    langchain_messages = []
    n = 0
    for msg in history:
        role = msg["role"]
        if role not in {"user", "assistant"}:
            continue
        content = msg["content"]
        if isinstance(content, list):
            content = "\n".join(
                block["text"]
                for block in content
                if isinstance(block, dict)
                and block.get("type") == "text"
                and isinstance(block.get("text"), str)
            )
        if not isinstance(content, str) or not content:
            continue
        if role == "user":
            langchain_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            langchain_messages.append(AIMessage(content=content))
            n += 1
    langchain_messages.append(HumanMessage(content=message))

    state = {"messages": langchain_messages, "llm_calls": n}
    response = llm.invoke(state)
    return response["messages"][-1].content


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _logs.info("Starting Assignment 2 App...")
    chat = gr.ChatInterface(
        fn=assignment_chat,
        chatbot=gr.Chatbot(render_markdown=True, placeholder="#### Sample Prompts"),
        title="Assignment 2 Chat",
        description="Welcome to Assignment 2 Chat! Please enter questions about countries, the Blue Cross book, or recent web topics, and I will provide a concise answer.  \nFor Country Information, you can ask about Capitals, Regions, Alpha Codes, and Calling Codes.",
        examples=[
            "Show the capital, region and alpha codes for Canada",
            "Provide a summary of the book 'The Blue Cross' by G.K. Chesterton",
            "Search the web for the latest headlines and summarize them briefly",
        ],
        cache_examples=False,
    )
    chat.launch(share=False)
