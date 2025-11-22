#!/usr/bin/env python3
"""
JSON to Vector Database Converter
Converts Confluence JSON data to vector embeddings and stores in ChromaDB
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any

# Add project root to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.core.rag.vector_store import VectorStore

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JSONToVectorConverter:
    def __init__(self, vector_db_path: str = "./data/chroma_db", collection_name: str = "team_knowledge"):
        """
        Initialize the converter with vector database configuration

        Args:
            vector_db_path: Path to ChromaDB storage
            collection_name: Name of the collection to store documents
        """
        self.vector_db_path = vector_db_path
        self.collection_name = collection_name
        self.vector_store = None

    def initialize_vector_store(self):
        """Initialize the vector store and collection"""
        try:
            logger.info(f"Initializing vector store at {self.vector_db_path}")
            self.vector_store = VectorStore(persist_directory=self.vector_db_path)
            self.vector_store.create_or_get_collection(self.collection_name)
            logger.info(f"Vector store initialized with collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize vector store: {e}")
            raise

    def load_json_file(self, json_file_path: str) -> List[Dict[str, Any]]:
        """
        Load and validate JSON file

        Args:
            json_file_path: Path to the JSON file

        Returns:
            List of document dictionaries
        """
        try:
            logger.info(f"Loading JSON file: {json_file_path}")
            with open(json_file_path, 'r', encoding='utf-8') as f:
                documents = json.load(f)

            if not isinstance(documents, list):
                raise ValueError("JSON file must contain a list of documents")

            logger.info(f"Loaded {len(documents)} documents from JSON file")
            return documents

        except FileNotFoundError:
            logger.error(f"JSON file not found: {json_file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading JSON file: {e}")
            raise

    def validate_document_format(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Validate that documents have required fields

        Args:
            documents: List of document dictionaries

        Returns:
            True if all documents are valid
        """
        required_fields = ['id', 'content']

        for i, doc in enumerate(documents):
            if not isinstance(doc, dict):
                logger.error(f"Document {i} is not a dictionary")
                return False

            for field in required_fields:
                if field not in doc:
                    logger.error(f"Document {i} missing required field: {field}")
                    return False

            if not doc['content'].strip():
                logger.warning(f"Document {i} has empty content")

        logger.info("All documents passed validation")
        return True

    def convert_and_store(self, json_file_path: str, clear_existing: bool = False) -> bool:
        """
        Convert JSON documents to vectors and store in database

        Args:
            json_file_path: Path to the JSON file
            clear_existing: Whether to clear existing documents first

        Returns:
            True if conversion was successful
        """
        try:
            # Initialize vector store
            self.initialize_vector_store()

            # Load documents
            documents = self.load_json_file(json_file_path)

            # Validate document format
            if not self.validate_document_format(documents):
                logger.error("Document validation failed")
                return False

            # Clear existing documents if requested
            if clear_existing:
                logger.info("Clearing existing documents...")
                try:
                    # Get current document IDs and delete them
                    collection_info = self.vector_store.get_collection_info()
                    if collection_info['count'] > 0:
                        # Note: ChromaDB doesn't have a clear all method, so we'd need to delete by IDs
                        logger.warning("Clear existing not fully implemented - continuing with add")
                except Exception as e:
                    logger.warning(f"Could not clear existing documents: {e}")

            # Add documents to vector store
            logger.info(f"Adding {len(documents)} documents to vector database...")
            self.vector_store.add_documents(documents)

            # Verify storage
            collection_info = self.vector_store.get_collection_info()
            logger.info(f"✅ Conversion completed successfully!")
            logger.info(f"Collection '{collection_info['name']}' now contains {collection_info['count']} documents")

            return True

        except Exception as e:
            logger.error(f"❌ Conversion failed: {e}")
            return False

    def test_search(self, query: str = "order processor", n_results: int = 3):
        """
        Test search functionality with the stored vectors

        Args:
            query: Test search query
            n_results: Number of results to return
        """
        if not self.vector_store:
            logger.error("Vector store not initialized")
            return

        try:
            logger.info(f"Testing search with query: '{query}'")
            results = self.vector_store.search(query, n_results=n_results)

            logger.info(f"Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                title = result.get('metadata', {}).get('title', 'No title')
                content_preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
                logger.info(f"  {i}. {title}")
                logger.info(f"     Preview: {content_preview}")
                if result.get('distance'):
                    logger.info(f"     Distance: {result['distance']:.4f}")
                logger.info("")

        except Exception as e:
            logger.error(f"Search test failed: {e}")

def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Convert JSON documents to vector database')
    parser.add_argument('json_file', help='Path to JSON file containing documents')
    parser.add_argument('--vector-db-path', default='./data/chroma_db',
                       help='Path to vector database directory (default: ./data/chroma_db)')
    parser.add_argument('--collection-name', default='team_knowledge',
                       help='Collection name (default: team_knowledge)')
    parser.add_argument('--clear-existing', action='store_true',
                       help='Clear existing documents before adding new ones')
    parser.add_argument('--test-search', help='Test search with given query after conversion')

    args = parser.parse_args()

    # Create converter
    converter = JSONToVectorConverter(
        vector_db_path=args.vector_db_path,
        collection_name=args.collection_name
    )

    # Perform conversion
    success = converter.convert_and_store(
        json_file_path=args.json_file,
        clear_existing=args.clear_existing
    )

    if success and args.test_search:
        converter.test_search(args.test_search)

    return 0 if success else 1

# Example usage functions
def convert_confluence_data():
    """Convert the specific Confluence data file"""
    json_file_path = "/home/zhumoore/projects/team-agent/data/jason/Software_dev_confluence_data.json"
    vector_db_path = "/home/zhumoore/projects/team-agent/data/chroma_db"

    converter = JSONToVectorConverter(
        vector_db_path=vector_db_path,
        collection_name="team_knowledge"
    )

    success = converter.convert_and_store(json_file_path)

    if success:
        # Test the conversion
        converter.test_search("order processor service")
        converter.test_search("notification dispatcher")

    return success

if __name__ == "__main__":
    # You can either run with command line args or use the direct function
    if len(sys.argv) > 1:
        exit_code = main()
        sys.exit(exit_code)
    else:
        # Direct conversion of your specific file
        print("🚀 Converting Confluence JSON to Vector Database...")
        print("=" * 60)
        success = convert_confluence_data()
        if success:
            print("🎉 Conversion completed successfully!")
        else:
            print("❌ Conversion failed!")