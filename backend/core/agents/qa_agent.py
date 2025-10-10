# agents/qa_agent.py
from datetime import datetime
from typing import Dict
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
import chromadb
# backend/core/rag/vector_store.py
# from backend.core.rag import VectorStore
from langchain_ollama import OllamaEmbeddings



class QAAgent:
    def __init__(self, chroma_db_path="data/chroma_db", ollama_model="qwen3:4b", ollama_base_url="http://localhost:11434"):
        self.vector_store = self._init_chroma_db(chroma_db_path)
        self.llm = self._init_ollama_llm(ollama_model, ollama_base_url)
        self.qa_chain = self._init_qa_chain()

    def _init_chroma_db(self, db_path):
        client = chromadb.PersistentClient(path=db_path)
        return Chroma(
            client=client,
            collection_name="team_knowledge"
        )

    def _init_ollama_llm(self, model, base_url):
        return OllamaLLM(
            model=model,
            base_url=base_url,
            temperature=0.7
        )
    
    def _init_qa_chain(self):
        prompt_template = """You are a helpful assistant for a software development team. 
        Use the following context to answer the question. If you don't know the answer, 
        just say you don't know. Always mention the source of your information.
        
        Context: {context}
        Question: {question}
        
        Answer: """
        
        PROMPT = PromptTemplate(
            template=prompt_template, 
            input_variables=["context", "question"]
        )
        
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(),
            chain_type_kwargs={"prompt": PROMPT}
        )
    
    def ask(self, question: str) -> Dict:
        """回答问题"""
        result = self.qa_chain.run(question)
        return {
            "question": question,
            "answer": result,
            "timestamp": datetime.now().isoformat()
        }
    
# Example usage
# vector_store = VectorStore(persist_directory="./data/chroma_db")

    # Create or get a collection
# collection = vector_store.create_or_get_collection("team_knowledge")
agent = QAAgent(chroma_db_path="data/chroma_db", ollama_model="qwen3:4b")
result = agent.ask("What is web3?")
print(f"Question: {result['question']}")
print(f"Answer: {result['answer']}")
print(f"Time: {result['timestamp']}")
