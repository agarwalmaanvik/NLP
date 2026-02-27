import os
import time
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader, JSONLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.vectorstore import MilvusHybridStore 

def run_ingestion():
    store = MilvusHybridStore() 
    internal_store = getattr(store, 'store', getattr(store, 'vector_store', None))

    if internal_store:
        try:
            internal_store.col.delete(expr="pk >= 0") 
            time.sleep(1) 
        except Exception as e:
            print(f"Error clearing existing data: {e}")
    processed_docs = []
    data_dir = "data"

    pdf_path = os.path.join(data_dir, "annual_report")
    if os.path.exists(pdf_path):
        for file in os.listdir(pdf_path):
            if file.endswith(".pdf"):
                loader = PyPDFLoader(os.path.join(pdf_path, file))
                processed_docs.extend(loader.load())

    other_loader = DirectoryLoader(
        os.path.join(data_dir, "hr_docs"),
        glob="**/*.txt",
        loader_cls=TextLoader
    )
    processed_docs.extend(other_loader.load())

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=100,
        add_start_index=True 
    )
    final_chunks = text_splitter.split_documents(processed_docs)

    # 5. ЗАГРУЗКА В MILVUS
    if final_chunks:
        store.build_from_documents(final_chunks)

if __name__ == "__main__":
    run_ingestion()