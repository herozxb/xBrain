import ollama
import ollama
import ollama

model_name = "deepseek-coder-v2"  # Assuming this is the correct model name, adjust if necessary
prompt = "Your prompt here"  # Replace with your actual prompt

response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])

def sample_function():
    model_name = "deepseek-coder-v2"  # Replace with the correct model name if known, otherwise leave it as is or ask for clarification
    prompt = "Your prompt here"  # Replace with the actual prompt used by the user
    
    response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
    suggested_code = response['message']['content']