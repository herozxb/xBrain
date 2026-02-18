from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.load_local("my_wiki_index", embeddings, allow_dangerous_deserialization=True)

# Access the internal documents
print(f"Total chunks in index: {len(vectorstore.docstore._dict)}")

# Print the first 5 entries
for i, (doc_id, doc) in enumerate(list(vectorstore.docstore._dict.items())[:615]):
    print(f"\n--- Chunk {i} ---\n{doc.page_content[:200]}...")
