import os
from FlagEmbedding import FlagReranker
from src.vectorstore import MilvusHybridStore
from langchain_google_genai import ChatGoogleGenerativeAI # Or ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

class RAGSearch:
    def __init__(self, uri="./milvus_demo.db", rerank_model="BAAI/bge-reranker-v2-m3"):
        self.vectorstore = MilvusHybridStore(uri=uri)
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
        self.reranker = None
        print("Loading Reranker (Memory Optimized)...")
        try:
            from FlagEmbedding import FlagReranker
            self.reranker = FlagReranker('BAAI/bge-reranker-v2-m3', use_fp16=True)
        except Exception as e:
            print(f"Reranker failed to load due to memory: {e}")
            print("Falling back to standard Semantic Retrieval.")

    def get_answer(self, query: str):
        initial_hits = self.vectorstore.hybrid_search(query, top_k=10)
        
        if not initial_hits:
            return "I couldn't find any relevant information.", []

        initial_results = []
        for hit in initial_hits:
            metadata = getattr(hit, 'metadata', {})
            initial_results.append({
                "text": hit.entity.get("text"),
                "source": hit.entity.get("source"),
                "score": hit.score
            })

        passages = [res['text'] for res in initial_results]
        rerank_pairs = [[query, p] for p in passages]
        rerank_scores = self.reranker.compute_score(rerank_pairs)
        
        for i, res in enumerate(initial_results):
            res['rerank_score'] = rerank_scores[i]
        
        final_results = sorted(initial_results, key=lambda x: x['rerank_score'], reverse=True)[:3]

        context = "\n\n".join([f"Source: {r['source']}\nContent: {r['text']}" for r in final_results])
        
        prompt = f"""
        You are a professional Enterprise Assistant. Use the context below to answer the user query.
        If the answer is from the Annual Report, you MUST mention the source metadata provided.
        
        Context:
        {context}
        
        User Query: {query}
        
        Answer:"""
        
        response = self.llm.invoke(prompt)
        return response.content, final_results