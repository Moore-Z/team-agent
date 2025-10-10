# Example usage of VectorStore class with document chunking
from sqlalchemy import null
from vector_store import VectorStore
import json
from typing import List, Dict, Any
import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def chunk_text(text: str, max_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks."""
    if len(text) <= max_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + max_size

        # Try to break at sentence boundaries
        if end < len(text):
            # Look for sentence endings within the last 200 chars
            search_start = max(start + max_size - 200, start)
            sentence_end = text.rfind('.', search_start, end)
            if sentence_end == -1:
                sentence_end = text.rfind('。', search_start, end)  # Chinese period
            if sentence_end != -1:
                end = sentence_end + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position with overlap
        start = end - overlap if end < len(text) else len(text)

    return chunks

def chunk_documents(documents: List[Dict[str, Any]], max_size: int = 1000, overlap: int = 200) -> List[Dict[str, Any]]:
    """Chunk documents that are too long."""
    chunked_documents = []

    for doc in documents:
        if isinstance(doc, dict) and 'content' in doc:
            content = doc.get('content', '')

            if len(content) <= max_size:
                chunked_documents.append(doc)
                continue

            # Split content into chunks
            text_chunks = chunk_text(content, max_size, overlap)

            for i, chunk in enumerate(text_chunks):
                if chunk.strip():  # Skip empty chunks
                    chunk_doc = {
                        'id': f"{doc.get('id', 'doc')}_chunk_{i}",
                        'content': chunk.strip(),
                        'metadata': {
                            **doc.get('metadata', {}),
                            'chunk_index': i,
                            'total_chunks': len(text_chunks),
                            'original_id': doc.get('id', 'doc'),
                            'chunk_type': 'text'
                        }
                    }
                    chunked_documents.append(chunk_doc)
        else:
            chunked_documents.append(doc)

    return chunked_documents

def main():
    # Initialize the vector store
    vector_store = VectorStore(persist_directory="./data/chroma_db")

    # Create or get a collection
    collection = vector_store.create_or_get_collection("team_knowledge")

    # Sample documents to add

    file_path = "data/jason/test_confluence_data.json"
    data = None
    try :
        with open(file_path,'r') as file:
            data = json.load(file)
        print("Json data load successfully")

    except FileNotFoundError:
        print(f"Error: the file '{file_path}' was not found")
        return
    except json.JSONDecodeError:
        print(f"Failed to decode JSON from the file '{file_path}'. Check for malformed JSON.")
        return
    except Exception as e:
        print(f"An unexcepted Error occured: {e}")
        return

    if data is None:
        print("No data loaded, exiting")
        return

    # Process documents and chunk if needed
    if isinstance(data, list):
        documents = data
    else:
        documents = [data]

    # Show original document sizes
    for doc in documents:
        if isinstance(doc, dict) and 'content' in doc:
            content_length = len(doc.get('content', ''))
            print(f"Document {doc.get('id', 'unknown')} content length: {content_length}")

    # Chunk documents that are too long
    processed_documents = chunk_documents(documents, max_size=1000, overlap=200)

    print(f"Original documents: {len(documents)}")
    print(f"Processed documents (after chunking): {len(processed_documents)}")

    # Add processed documents to the vector store
    vector_store.add_documents(processed_documents)

    # Search for similar documents
    search_results = vector_store.search("web3", n_results=2)
    print("Search results:")
    for result in search_results:
        print(f"ID: {result['id']}")
        print(f"Content: {result['content']}")
        print(f"Metadata: {result['metadata']}")
        print(f"Distance: {result['distance']}")
        print("-" * 50)

    # Search with metadata filtering
    filtered_results = vector_store.search(
        "web3",
        n_results=2,
        where={"type": "programming"}
    )
    print("\nFiltered search results:")
    for result in filtered_results:
        print(f"ID: {result['id']}")
        print(f"Content: {result['content']}")
        print("-" * 50)

    # Get collection information
    info = vector_store.get_collection_info()
    print(f"\nCollection info: {info}")

    # Update a document
    # updated_docs = [
    #     {
    #         'id': 'doc1',
    #         'content': 'Updated content about advanced machine learning and deep learning',
    #         'metadata': {'type': 'technical', 'category': 'AI', 'updated': True}
    #     }
    # ]
    # vector_store.update_documents(updated_docs)

    # Delete documents
    # vector_store.delete_documents(['doc3'])

if __name__ == "__main__":
    main()