import ollama  # Importing the necessary library for chat functionality

def sample_function():
    prompt = "write hello world"  # Defining the prompt to be sent to the chat model
    
    # Sending the prompt to the DeepSeek Coder V2 via Ollama's chat method
    response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
    
    # Extracting and assigning the suggested code from the response
    suggested_code = response['message']['content']