import os
from FlagEmbedding import FlagReranker
from src.vectorstore import MilvusHybridStore
from langchain_google_genai import ChatGoogleGenerativeAI # Or ChatGroq

class RAGSearch:
    def __init__(self, uri="./milvus_demo.db", rerank_model="BAAI/bge-reranker-v2-m3"):
        # 1. Connect to your Milvus Hybrid Store
        self.vectorstore = MilvusHybridStore(uri=uri)
        
        # 2. Initialize the Cross-Encoder Reranker
        # This is the "Judge" that re-scores the retrieved snippets
        self.reranker = FlagReranker(rerank_model, use_fp16=True)
        
        # 3. Initialize the LLM (Gemini or Groq)
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        print(f"[INFO] Reranker and LLM initialized.")

    def get_answer(self, query: str):
        # STAGE 1: Hybrid Retrieval (Retrieves 10 candidate chunks)
        initial_results = self.vectorstore.hybrid_search(query, top_k=10)
        
        # STAGE 2: Re-ranking
        # We pair the query with each retrieved text for the reranker to score
        passages = [res['entity']['text'] for res in initial_results]
        rerank_pairs = [[query, p] for p in passages]
        rerank_scores = self.reranker.compute_score(rerank_pairs)
        
        # Combine scores and sort to get the absolute top 3
        for i, res in enumerate(initial_results):
            res['rerank_score'] = rerank_scores[i]
        
        # Sort by reranker score (highest first)
        final_results = sorted(initial_results, key=lambda x: x['rerank_score'], reverse=True)[:3]

        # STAGE 3: Context Preparation & Generation
        context = "\n\n".join([f"Source: {r['entity']['source']}\nContent: {r['entity']['text']}" for r in final_results])
        
        prompt = f"""
        You are a professional Enterprise Assistant. Use the context below to answer the user query.
        If the answer is from the Annual Report, you MUST mention the source metadata provided.
        
        Context:
        {context}
        
        User Query: {query}
        
        Answer:"""
        
        response = self.llm.invoke(prompt)
        return response.content, final_results