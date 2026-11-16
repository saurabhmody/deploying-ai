from pathlib import Path
from openai import OpenAI
import os
import chromadb
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv(".env")
load_dotenv(".secrets")

USE_GATEWAY = (os.getenv('USE_GATEWAY', 'FALSE').upper() == 'TRUE')
MODEL = os.getenv('MODEL', 'gpt-4o-mini')
EMBEDDING_MODEL = "text-embedding-3-small"

# Set up the OpenAI client based on the USE_GATEWAY environment variable
def get_client(use_gateway: bool = USE_GATEWAY) -> OpenAI:
    if use_gateway:
        client = OpenAI(base_url='https://k7uffyg03f.execute-api.us-east-1.amazonaws.com/prod/openai/v1',
                    api_key=os.getenv('OPENAI_API_KEY'),
                    default_headers={"x-api-key": os.getenv('API_GATEWAY_KEY')})
    else:
        client = OpenAI()
    return client

client = get_client()

PARENT_DIR = Path(__file__).resolve().parent
DOCUMENT_PATH = PARENT_DIR.parent / "documents" / "chesterton" / "the_blue_cross.txt"
DATABASE_PATH = PARENT_DIR / "chroma_data"

chroma_client = chromadb.PersistentClient(path=str(DATABASE_PATH))
collection = chroma_client.get_or_create_collection(
    name="blue_cross_document",
    metadata={"description": "The Blue Cross by G.K. Chesterton"},
)
existing_ids = collection.get(include=[])["ids"]
if existing_ids:
    collection.delete(ids=existing_ids)
print(f"Cleared {len(existing_ids)} existing record(s) from 'blue_cross_document'.")

document_text = DOCUMENT_PATH.read_text(encoding="utf-8")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=3000,
    chunk_overlap=300,
    separators=["\n\n", "\n", " ", ""],
)
chunks = text_splitter.split_text(document_text)

embedding_response = client.embeddings.create(
    input=chunks,
    model=EMBEDDING_MODEL,
)
embedding_data = sorted(embedding_response.data, key=lambda item: item.index)
embeddings = [item.embedding for item in embedding_data]

collection.upsert(
    ids=[f"{DOCUMENT_PATH.stem}-{index}" for index in range(len(chunks))],
    documents=chunks,
    embeddings=embeddings,
    metadatas=[{"source": DOCUMENT_PATH.name, "chunk": index} for index in range(len(chunks))],
)

print(f"Loaded {len(chunks)} chunks from '{DOCUMENT_PATH.name}' into the ChromaDB collection 'blue_cross_document'.")
