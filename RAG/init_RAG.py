from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA

# 1. Initialize the LLM (Running via Ollama on your M3 GPU)
llm = Ollama(model="deepseek-coder-v2")

# 2. Setup Embeddings (Uses HuggingFace on your local CPU/GPU)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# 3. Create your data (Example text)
text = "The MacBook M3 uses a 3nm process and features a powerful Neural Engine for AI tasks."
text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
docs = text_splitter.create_documents([text])

# 4. Create Vector Store
vectorstore = FAISS.from_documents(docs, embeddings)

# 5. Create the RAG Chain
qa_chain = RetrievalQA.from_chain_type(
    llm,
    retriever=vectorstore.as_retriever()
)

# Save the database to a folder named 'my_faiss_index'
vectorstore.save_local("my_RAG_index")

# 6. Ask a question
question = "What process does the M3 chip use?"
print(qa_chain.invoke(question))
