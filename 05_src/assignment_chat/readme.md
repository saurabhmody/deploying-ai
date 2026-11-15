## Assignment Chat

This folder contains a small multi-tool chat app built around LangGraph, Gradio, OpenAI, and ChromaDB. The app supports following tools:

- Country information via the CountryLayer API
- Book retrieval for G.K. Chesterton's The Blue Cross via a ChromaDB vector database

The project is structured as a lightweight agent workflow: the LLM receives tool-enabled instructions, decides when to call tools, and formats a final response for the user. This app is designed to demonstrate how a chat interface can combine prompt instructions, external APIs, and semantic retrieval.

## Files

## assignment2_main.py

This code creates the agent graph used by the app. It creates a chat model, registers the available tools, and defines a LangGraph state machine. This is the core of the agent: the LLM sees the prompt rules and can call tools when needed; after a tool call, the model is invoked again to reason over the tool result.

## assignment2_app.py

This code provides the Gradio web chat interface. It turns the user conversation into LangChain message objects so the LangGraph workflow can use prior chat history. It also defines the assignment_chat function that serves as the Gradio callback. It launches the UI which is designed to be conversational while still routing to the right tool.

## assignment2_load_chromadb.py

This code creates and populates a local ChromaDB vector store for The Blue Cross book. It loads the book text from the project documents folder into a persistent ChromaDB collection so the retrieval tool can do semantic search later. The load process reads the full book text and splits the document into chunks of 3000 characters with 300 characters overlap. Embeddings are created for each chunk and stored in ChromaDB along with the text and metadata. This creates a searchable semantic index where user questions can be compared against the embedded chunks rather than matching raw text exactly.

## assignment2_prompts.py

Defines the system instructions for the agent. The return_instructions() function centralizes the rules that govern the agent's behavior and keeps the application logic separate from the prompt logic.

## assignment2_tools_book.py

This code provides the retrieval tool used to answer questions about The Blue Cross. It embeds a user query using the same OpenAI embedding model and searches the ChromaDB collection for the most relevant text chunks. It returns the top relevant document chunks 


## assignment2_tools_country.py

This code defines the country lookup tool. It queries the CountryLayer API to return requested country fields such as capital, region, alpha codes, and calling codes.

