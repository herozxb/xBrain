import os
from langchain_community.llms import Ollama
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA

# --- INITIAL SETUP ---
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db_path = "my_RAG_index"
llm = Ollama(model="deepseek-coder-v2")

vectorstore = FAISS.load_local(db_path, embeddings, allow_dangerous_deserialization=True)

# Initialize the RAG Chain
qa_chain = RetrievalQA.from_chain_type(llm, retriever=vectorstore.as_retriever())

print("--- M3 RAG System Ready ---")
print("Instructions:")
print("- Just type your question to ask the AI.")
print("- Type 'ADD: [your text]' to add new knowledge.")
print("- Type 'exit' to quit.")

# --- INTERACTIVE LOOP ---
while True:
    user_input = input("\nUser > ").strip()
    
    if user_input.lower() in ['exit', 'quit']:
        break
    
    # Mode: Add new knowledge
    if user_input.startswith("ADD:"):
        new_content = user_input.replace("ADD:", "").strip()
        text_splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=0)
        new_docs = text_splitter.create_documents([new_content])
        
        vectorstore.add_documents(new_docs)
        vectorstore.save_local(db_path) # Persist to M3 disk immediately
        print(f"✅ Knowledge saved to {db_path}!")
        
        # Refresh the chain with new data
        qa_chain = RetrievalQA.from_chain_type(llm, retriever=vectorstore.as_retriever())

    # Mode: Question & Answer
    else:
        print("AI Thinking...")
        response = qa_chain.invoke(user_input)
        print(f"AI > {response['result']}")
