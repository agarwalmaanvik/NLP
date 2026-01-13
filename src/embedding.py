from FlagEmbedding import BGEM3FlagModel
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List, Any

class EmbeddingPipeline:
    def __init__(self, model_name: str = "BAAI/bge-m3", chunk_size: int = 1000, chunk_overlap: int = 200):
        # 1. Initialize the BGE-M3 specialized model
        # use_fp16=True makes it much faster if you have a GPU
        self.model = BGEM3FlagModel(model_name, use_fp16=True, normalize_embeddings=True)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        print(f"[INFO] BGE-M3 Model Loaded. Dimensions: 1024")

    def chunk_documents(self, documents: List[Any]) -> List[Any]:
        # Standard recursive splitting (Same as before)
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", " ", ""]
        )
        return splitter.split_documents(documents)

    def generate_hybrid_data(self, chunks: List[Any]):
        """
        The 'Magic' Function: Generates both Dense and Sparse representations.
        """
        texts = [chunk.page_content for chunk in chunks]
        
        # 2. Get the Multi-Function Output
        output = self.model.encode(
            texts, 
            return_dense=True,   # Semantic Vector
            return_sparse=True,  # Keyword Weights (BM25 style)
            return_colbert_vecs=False # We skip ColBERT to save memory
        )
        print(f"[DEBUG] Generated {len(output['dense_vecs'])} dense vectors and {len(output['lexical_weights'])} sparse vectors")
        # 3. Separate the results
        # dense_vecs: List of 1024-dimension arrays
        # lexical_weights: List of dictionaries { 'token_id': weight }
        return {
    "dense": output['dense_vecs'],
    "sparse": output['lexical_weights']
        }
    
    