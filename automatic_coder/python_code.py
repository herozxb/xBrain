import ollama

def sample_function():
    model_name = "deepseek-coder-v2"  # Replace with the actual model name if known, or retrieve it dynamically
    prompt = "write hello world"  # Replace with your actual prompt
    
    response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
    suggested_code = response['message']['content']