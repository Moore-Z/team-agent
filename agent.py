import os
from dotenv import load_dotenv
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from rich.console import Console
from rich.markdown import Markdown
from langchain_anthropic import ChatAnthropic

# --- 1. SETUP ---
# Load environment variables from .env file (for API keys)
load_dotenv()

# Set up the paths for the documentation and the persistent vector store
DOCS_DIR = "docs"
PERSIST_DIR = "persist"

# --- 2. THE CORE RAG LOGIC ---

def get_vector_store():
    """
    Creates or loads a persistent vector store from the documentation.
    This is optimized to only process documents once.
    """
    # Check if the vector store already exists
    if os.path.exists(PERSIST_DIR):
        # If it exists, load it from disk
        print("Loading existing vector store from disk...")
        vector_store = Chroma(
            persist_directory=PERSIST_DIR,
            embedding_function=HuggingFaceEmbeddings()
        )
    else:
        # If it doesn't exist, create it
        print("Creating new vector store...")
        # Load documents from the specified directory
        loader = DirectoryLoader(DOCS_DIR, glob="**/*.md") # Assumes Markdown files
        documents = loader.load()

        # Split the documents into smaller chunks for better retrieval
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        texts = text_splitter.split_documents(documents)

        # Create the vector store with OpenAI embeddings and persist it
        vector_store = Chroma.from_documents(
            documents=texts,
            embedding=HuggingFaceEmbeddings(),
            persist_directory=PERSIST_DIR
        )
        print(f"Vector store created and saved to {PERSIST_DIR}.")
    
    return vector_store

# --- 3. THE INTERACTIVE CLI ---

def main():
    """
    The main function that runs the interactive command-line interface.
    """
    console = Console()
    console.print("[bold green]Welcome to the Team Info Agent![/bold green]")
    console.print("Ask a question about the team's documentation, or type 'exit' to quit.")

    # Get the vector store (this will be our knowledge base)
    vector_store = get_vector_store()

    # Set up the LLM and the retrieval chain
    # llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm,
        vector_store.as_retriever(search_kwargs={"k": 2}), # Retrieve top 2 results
        return_source_documents=True
    )

    chat_history = []

    # The main chat loop
    while True:
        query = input("\n> ")
        if query.lower() in ["exit", "quit"]:
            break

        # Get the result from the chain
        result = qa_chain.invoke({"question": query, "chat_history": chat_history})
        answer = result["answer"]

        # Update chat history for conversation context
        chat_history.append((query, answer))

        # Print the answer using Rich for nice formatting
        console.print("\n[bold green]Answer:[/bold green]")
        console.print(Markdown(answer))
        
        # Optionally, print the sources it used to generate the answer
        console.print("\n[bold yellow]Sources Used:[/bold yellow]")
        for doc in result["source_documents"]:
            console.print(f"- {doc.metadata.get('source', 'Unknown')}")


if __name__ == "__main__":
    main()
