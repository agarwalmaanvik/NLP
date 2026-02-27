import os
from pymilvus import MilvusClient, DataType, AnnSearchRequest, WeightedRanker
from src.embedding import EmbeddingPipeline

class MilvusHybridStore:
    def __init__(self, uri="./milvus_demo.db", collection_name="enterprise_knowledge"):
        self.client = MilvusClient(
    uri="https://in03-857c25d478acdc2.serverless.aws-eu-central-1.cloud.zilliz.com", 
    token="4209abb1ee33d25180761796f0c81723d31e881808030ad8e21dd229daf30902f515499de78ef2f35e6b541c1cd440b8c719f2fa"
)
        self.collection_name = collection_name
        self.emb_pipe = EmbeddingPipeline()

        if not self.client.has_collection(collection_name):
            schema = self.client.create_schema(auto_id=True, enable_dynamic_field=True)
            schema.add_field(field_name="pk", datatype=DataType.INT64, is_primary=True)
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)
            schema.add_field(field_name="dense_vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
            schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
            
            index_params = self.client.prepare_index_params()
            index_params.add_index(field_name="dense_vector", index_type="FLAT", metric_type="IP")
            index_params.add_index(field_name="sparse_vector", index_type="SPARSE_INVERTED_INDEX", metric_type="IP")
            
            self.client.create_collection(collection_name=collection_name, schema=schema, index_params=index_params)

    def build_from_documents(self, documents):
        chunks = self.emb_pipe.chunk_documents(documents)
        hybrid_data = self.emb_pipe.generate_hybrid_data(chunks)
        
        entities = []
        for i, chunk in enumerate(chunks):
            entities.append({
                "text": chunk.page_content,
                "dense_vector": hybrid_data["dense"][i],
                "sparse_vector": hybrid_data["sparse"][i],
                "source": chunk.metadata.get("source", "")
            })
        
        self.client.insert(collection_name=self.collection_name, data=entities)

    def hybrid_search(self, query, top_k=5):
        query_data = self.emb_pipe.generate_hybrid_data([type('obj', (object,), {'page_content': query})])
        dense_req = AnnSearchRequest(query_data["dense"], "dense_vector", {"metric_type": "IP"}, limit=top_k)
        sparse_req = AnnSearchRequest(query_data["sparse"], "sparse_vector", {"metric_type": "IP"}, limit=top_k)
    
        results = self.client.hybrid_search(
            collection_name=self.collection_name,
            reqs=[dense_req, sparse_req],
            ranker=WeightedRanker(0.7, 0.3),
            limit=top_k,
            output_fields=["text", "source"]
        )
        return results[0]