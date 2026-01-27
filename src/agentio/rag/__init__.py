import abc
from typing import List

class RAGRetriever(abc.ABC):
    @abc.abstractmethod
    async def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        pass

class SimpleRAG(RAGRetriever):
    def __init__(self, documents: List[str]):
        self.documents = documents

    async def retrieve(self, query: str, top_k: int = 3) -> List[str]:
        # Dummy keyword matching
        results = [doc for doc in self.documents if any(word in doc.lower() for word in query.lower().split())]
        return results[:top_k]
