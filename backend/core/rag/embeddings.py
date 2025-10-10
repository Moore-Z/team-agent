from langchain.embeddings import OpenAIEmbeddings
from typing import List, Optional
import hashlib

class EmbeddingManager:
    def __init__(self, model: str = "text-embedding-ada-002"):
        self.embeddings = OpenAIEmbeddings(model=model)
        self._cache = {}  # 简单的内存缓存
    
    def get_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        if use_cache:
            text_hash = hashlib.md5(text.encode()).hexdigest()
            if text_hash in self._cache:
                return self._cache[text_hash]
        
        embedding = self.embeddings.embed_query(text)
        if use_cache:
            self._cache[text_hash] = embedding
        return embedding