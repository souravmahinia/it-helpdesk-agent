import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

# Path to your IT policy document
POLICY_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "it_policy.txt"
)

# Path where ChromaDB will save embeddings permanently on disk
CHROMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data", "chroma_db"
)


def build_rag_pipeline():
    """
    Builds the RAG pipeline — runs ONCE to create the vector database.
    
    Flow:
    1. Load IT policy document
    2. Split into chunks
    3. Convert chunks to embeddings
    4. Save to ChromaDB on disk (persisted)
    
    After this runs once, we never need to run it again
    unless the policy document changes.
    """

    print("\n🔧 Building RAG pipeline...")

    # STEP 1 — Load the IT policy document
    # TextLoader reads your .txt file
    print("📄 Loading IT policy document...")
    loader = TextLoader(POLICY_PATH, encoding="utf-8")
    documents = loader.load()
    print(f"✅ Document loaded — {len(documents)} pages")

    # STEP 2 — Split into chunks
    # We split by 500 characters with 50 character overlap
    # Overlap means chunks share some text — this helps
    # RAG find relevant content even if it spans two chunks
    print("✂️ Splitting document into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(documents)
    print(f"✅ Created {len(chunks)} chunks from policy document")

    # STEP 3 + 4 — Convert to embeddings AND save to disk
    # OpenAIEmbeddings converts text to numbers
    # Chroma.from_documents saves them permanently to disk
    print("🧠 Converting chunks to embeddings and saving to ChromaDB...")
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    # This one line does both — embeds AND saves to disk
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )

    print(f"✅ RAG pipeline built! {len(chunks)} chunks saved to ChromaDB")
    print(f"📁 ChromaDB saved at: {CHROMA_PATH}")
    return vectorstore


def load_rag_pipeline():
    """
    Loads existing ChromaDB from disk.
    This is what we call every time a ticket comes in.
    No re-embedding needed — just load and search.
    """
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )

    vectorstore = Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

    return vectorstore


def get_relevant_policy(ticket_description, k=2):
    """
    Searches ChromaDB for the most relevant policy sections
    for a given ticket description.
    
    k=2 means return top 2 most relevant chunks.
    In production you might use k=3 for more context.
    """

    # Check if ChromaDB exists — if not, build it first
    if not os.path.exists(CHROMA_PATH):
        print("ChromaDB not found — building RAG pipeline first...")
        build_rag_pipeline()

    # Load from disk
    vectorstore = load_rag_pipeline()

    # Search for relevant policy sections
    # This converts ticket to embeddings and finds closest matches
    relevant_chunks = vectorstore.similarity_search(
        ticket_description,
        k=k
    )

    # Combine the relevant chunks into one string
    policy_context = "\n\n".join([chunk.page_content for chunk in relevant_chunks])

    return policy_context


# Test the RAG pipeline
if __name__ == "__main__":
    # First build the pipeline
    build_rag_pipeline()

    # Test with a sample ticket
    print("\n🔍 Testing RAG search...")
    test_ticket = "I need access to the Finance system for my project"
    
    print(f"Ticket: {test_ticket}")
    print("\nRelevant Policy Found:")
    policy = get_relevant_policy(test_ticket)
    print(policy)


# 🔧 Building RAG pipeline...
# 📄 Loading IT policy document...
# ✅ Document loaded
# ✂️ Splitting into chunks...
# ✅ Created X chunks
# 🧠 Converting to embeddings...
# ✅ RAG pipeline built!

# 🔍 Testing RAG search...
# Ticket: I need access to the Finance system
# Relevant Policy Found:
# Finance system access requires both manager and Finance Head approval...