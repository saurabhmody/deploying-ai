import os

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import SystemMessage
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from assignment_chat.assignment2_prompts import return_instructions
from assignment_chat.assignment2_tools_book import search_blue_cross
from assignment_chat.assignment2_tools_country import get_country_info

_SOURCE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(_SOURCE_DIR, ".env"))
load_dotenv(os.path.join(_SOURCE_DIR, ".secrets"))

_MODEL_NAME = os.getenv("OPENAI_MODEL") or os.getenv("MODEL", "openai:gpt-4o-mini")
if ":" in _MODEL_NAME:
    _MODEL_PROVIDER, _MODEL_NAME = _MODEL_NAME.split(":", 1)
else:
    _MODEL_PROVIDER = "openai"

_MODEL_OPTIONS = {}
if os.getenv("USE_GATEWAY", "FALSE").upper() == "TRUE":
    _gateway_key = os.getenv("API_GATEWAY_KEY")
    if not _gateway_key:
        raise ValueError("Missing API_GATEWAY_KEY environment variable")
    _MODEL_OPTIONS.update(
        base_url="https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1",
        api_key=os.getenv("OPENAI_API_KEY") or "any value",
        default_headers={"x-api-key": _gateway_key},
    )

chat_agent = init_chat_model(
    _MODEL_NAME,
    model_provider=_MODEL_PROVIDER,
    **_MODEL_OPTIONS,
)
tools = [get_country_info, search_blue_cross]
instructions = return_instructions()


def call_model(state: MessagesState):
    response = chat_agent.bind_tools(tools).invoke(
        [SystemMessage(content=instructions), *state["messages"]]
    )
    return {"messages": [response]}


def get_graph():
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", tools_condition)
    builder.add_edge("tools", "call_model")
    return builder.compile()
