from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter

# 1. Setup Embeddings (Must be the same one used previously)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 2. Load the existing database
vectorstore = FAISS.load_local("my_RAG_index", embeddings, allow_dangerous_deserialization=True)

# 3. Prepare your NEW data
new_text = "The M3 Max chip supports up to 128GB of unified memory."
text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
new_docs = text_splitter.create_documents([new_text])

# 4. ADD the new data to the existing vectorstore
vectorstore.add_documents(new_docs)

# 5. SAVE the updated database back to the folder
vectorstore.save_local("my_RAG_index")

print("Knowledge base updated successfully!")
