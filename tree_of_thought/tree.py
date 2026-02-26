import ollama
import sys

# We check if we are accidentally importing the wrong thing
if not hasattr(ollama, 'chat'):
    print("CRITICAL ERROR: Python is still importing a local file as 'ollama'.")
    print("Check for any files named 'ollama.py' in your folder and delete them.")
    sys.exit(1)

MODEL = "deepseek-coder-v2:latest"

def simulate_reasoning():
    question = "What is the area of a triangle with base 5 and height 5?"
    print(f"\n[SYSTEM] Question: {question}")
    
    # 1. GENERATE BRANCHES
    print("[THINKING] Generating Branch 1...")
    # Using chat() is the correct method for current ollama-python library
    response = ollama.chat(model=MODEL, messages=[
        {'role': 'user', 'content': f"Solve this step-by-step: {question}"}
    ])
    thought = response['message']['content']
    
    # 2. VERIFY
    print("[VERIFYING] Checking logic...")
    verify_response = ollama.chat(model=MODEL, messages=[
        {'role': 'user', 'content': f"Is this math correct? Answer ONLY with 'YES' or 'NO': {thought}"}
    ])
    
    is_correct = verify_response['message']['content']
    
    print("-" * 30)
    print(f"INTERNAL VALIDATION: {is_correct}")
    print(f"FINAL ANSWER: {thought}")

if __name__ == "__main__":
    simulate_reasoning()

