# agents/qa_agent.py
from datetime import datetime
from typing import Dict, List
from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_chroma import Chroma
import chromadb
# backend/core/rag/vector_store.py
# from backend.core.rag import VectorStore
from langchain_ollama import OllamaEmbeddings
from backend.core.rag.benchmark_system import ConfluenceBenchmark, TestCase



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
            temperature=0.1,
            top_p=0.3,
            num_predict=30
        )
    
    def _init_qa_chain(self):
        prompt_template = """Answer the question using ONLY the given context.
        Give a direct, factual answer in 5 words or less.
        If not in context, answer: "Information not available"

        Context: {context}
        Question: {question}
        Answer:"""
        
        PROMPT = PromptTemplate(
            template=prompt_template, 
            input_variables=["context", "question"]
        )
        
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 2}),
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
    
    def ask(self, question: str) -> Dict:
        """Answer questions"""
        result = self.qa_chain.invoke({"query": question})

        # Extract retrieved context and evidence
        source_documents = result.get("source_documents", [])
        retrieved_context = []
        evidence = []

        for i, doc in enumerate(source_documents):
            # Add retrieved text content
            retrieved_context.append({
                "chunk_id": i + 1,
                "content": doc.page_content,
                "relevance_score": getattr(doc, 'relevance_score', None)
            })

            # Add source evidence metadata
            metadata = doc.metadata
            evidence.append({
                "source_id": i + 1,
                "source": metadata.get("source", "Unknown"),
                "page": metadata.get("page", None),
                "chunk_size": len(doc.page_content)
            })

        return {
            "question": question,
            "answer": result["result"],
            "retrieved_context": retrieved_context,
            "evidence": evidence,
            "timestamp": datetime.now().isoformat()
        }
    

# agent = QAAgent(chroma_db_path="data/chroma_db", ollama_model="llama2:latest")
# benchmark = ConfluenceBenchmark()
# cases = benchmark.test_cases
# # for test in cases[:1]:
# for test in cases:

#     if test.difficulty=="EASY":
#         print(f"\nQuestion: {test.query}")
#         result = agent.ask(test.query)
#         print(f"\nExpected Answer: {test.expected_answer}")
#         print(f"Actual Answer: {result['answer']}")

        # # This part for debug  Context/RAG Contedxt
        # print(f"\nRetrieved Context ({len(result['retrieved_context'])} chunks):")
        # for i, context in enumerate(result['retrieved_context']):
        #     print(f"  Chunk {i+1}: {context['content'][:400]}...")

        # print(f"\nEvidence Sources:")
        # for evidence in result['evidence']:
        #     print(f"  Source: {evidence['source']}, Page: {evidence['page']}, Size: {evidence['chunk_size']} chars")

