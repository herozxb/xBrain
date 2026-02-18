from langchain_community.llms import Ollama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain.chains import RetrievalQA
import wikipediaapi

# 1. Setup Embeddings & LLM
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = Ollama(model="deepseek-coder-v2")


# 2. Get Wikipedia Data
wiki = wikipediaapi.Wikipedia(language='en', user_agent='RAG_Demo/1.0')
page = wiki.page("Artificial Intelligence")

if page.exists():
    # Split text into clean chunks
    raw_sentences = [s.strip() for s in page.text.split('.') if len(s) > 20]
    # Convert strings to LangChain Document objects
    docs = [Document(page_content=s, metadata={"source": "wikipedia"}) for s in raw_sentences]
    print(f"Loaded {len(docs)} documents from Wikipedia.")
else:
    print("Wikipedia page not found!")
    exit()

# 3. Create/Merge Vector Store 
# LangChain's FAISS.from_documents automatically uses IndexFlatL2 (no training crash!)
vectorstore = FAISS.from_documents(docs, embeddings)

# 4. (Optional) Add your M3 text to the same database
m3_text = "The MacBook M3 uses a 3nm process and features a powerful Neural Engine."
vectorstore.add_texts([m3_text])

# 5. Create the RAG Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}) # Get top 3 snippets
)

# 6. Test it
question = "What is the relationship between the M3 chip and Artificial Intelligence?"
response = qa_chain.invoke(question)
print(f"\nAnswer:\n{response['result']}")

# Save for later
vectorstore.save_local("my_wiki_index")
