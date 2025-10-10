# core/rag/vector_store.py
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, persist_directory: str = "./data/chroma_db"):
        try:
            self.client = chromadb.PersistentClient(path=persist_directory)
            self.collection = None
            logger.info(f"Vector store initialized with directory: {persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise

    def create_or_get_collection(self, name: str = "team_knowledge"):
        try:
            self.collection = self.client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"Collection '{name}' created/retrieved successfully")
            return self.collection
        except Exception as e:
            logger.error(f"Failed to create/get collection '{name}': {e}")
            raise

    def add_documents(self, documents: List[dict]):
        if not self.collection:
            raise ValueError("Collection not initialized. Call create_or_get_collection first.")

        if not documents:
            logger.warning("No documents provided to add")
            return

        try:
            self.collection.add(
                documents=[doc['content'] for doc in documents],
                metadatas=[doc.get('metadata', {}) for doc in documents],
                ids=[doc['id'] for doc in documents]
            )
            logger.info(f"Added {len(documents)} documents to collection")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    def search(self, query: str, n_results: int = 5, where: Optional[Dict] = None) -> List[Dict[str, Any]]:
        if not self.collection:
            raise ValueError("Collection not initialized. Call create_or_get_collection first.")

        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where
            )

            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'][0] else {},
                        'distance': results['distances'][0][i] if results['distances'] else None
                    })

            logger.info(f"Search returned {len(formatted_results)} results")
            return formatted_results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise

    def delete_documents(self, ids: List[str]):
        if not self.collection:
            raise ValueError("Collection not initialized. Call create_or_get_collection first.")

        try:
            self.collection.delete(ids=ids)
            logger.info(f"Deleted {len(ids)} documents")
        except Exception as e:
            logger.error(f"Failed to delete documents: {e}")
            raise

    def update_documents(self, documents: List[dict]):
        if not self.collection:
            raise ValueError("Collection not initialized. Call create_or_get_collection first.")

        if not documents:
            logger.warning("No documents provided to update")
            return

        try:
            self.collection.update(
                documents=[doc['content'] for doc in documents],
                metadatas=[doc.get('metadata', {}) for doc in documents],
                ids=[doc['id'] for doc in documents]
            )
            logger.info(f"Updated {len(documents)} documents")
        except Exception as e:
            logger.error(f"Failed to update documents: {e}")
            raise

    def get_collection_info(self) -> Dict[str, Any]:
        if not self.collection:
            raise ValueError("Collection not initialized. Call create_or_get_collection first.")

        try:
            count = self.collection.count()
            return {
                'name': self.collection.name,
                'count': count,
                'metadata': self.collection.metadata
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            raise