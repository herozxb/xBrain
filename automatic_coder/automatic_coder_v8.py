import subprocess
import time
import ollama

# Initialize DeepSeek Coder V2 model
def get_deepseek_fix(error_output):
    # Use DeepSeek Coder V2 to suggest fixes based on the error output
    model_name = "deepseek-coder-v2:latest"  # Replace with your DeepSeek model name
    prompt = f"""Fix the following Python code error: {error_output}. 
    Suggest a solution for the issue.CODE QUALITY:
    - No explanatory text or comments
    - Production-ready code
    """

    try:
        print("# 3.1 Fixing the bug by the LLM of deepseek-coder-v2")
        # Sending the error message to DeepSeek Coder V2 for suggestions
        response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
        # Extracting the Python code from the response and ensuring it's wrapped in triple backticks with 'python'
        suggested_code = response['message']['content']
        if "```python" in suggested_code and "```" in suggested_code:
            # Extract code between ```python and closing ```
            start = suggested_code.find("```python") + len("```python")
            end = suggested_code.find("```", start)
            code = suggested_code[start:end].strip()
            return code
        else:
            # If no ```python``` block is found, return the full response
            return suggested_code
    except Exception as e:
        print(f"Error using DeepSeek Coder V2: {e}")
        return None

# Step 1: Generate Python code and save to a file
def generate_python_code():
    code = """
# This is the generated code for 1 + 1
 result = 1 + 1
 print(f"The result is: {result}")
    """
    with open("python_code.py", "w") as f:
        f.write(code)

# Step 2: Run the generated Python file
def run_python_file():
    try:
        result = subprocess.run(['python3', 'python_code.py'], capture_output=True, text=True)
        print("# 1.1 Output:", result.stdout)
        print("# 1.2 Error (if any):", result.stderr)
        return result
    except Exception as e:
        print(f"Error running Python file: {e}")
        return None

# Step 3: Capture and fix any potential bugs based on terminal output
def fix_bug(error_output):
    # Simulating a bug fix by adjusting the code to ensure it's always correct
    print("# 2.1 Fixing bug based on error output...")
    

    print(f"# 2.2 Detected error: {error_output}. Using DeepSeek Coder V2 to fix the issue.")
    fix_suggestion = get_deepseek_fix(error_output)

    if fix_suggestion:
        print(f"# 2.3 Suggested fix from DeepSeek Coder V2: {fix_suggestion}")
    
    with open("python_code.py", "w") as f:
        f.write(fix_suggestion)



# Main loop to generate, run, debug, fix, and repeat
def main():
    generate_python_code()  # Step 1: Generate code
    while True:
        
        result = run_python_file()  # Step 2: Run the code

        if result and result.stderr:
            # Step 3: If there's an error, capture the error and fix the bug
            print(f"Bug detected, error message: {result.stderr}")
            fix_bug(result.stderr)  # Pass the error message to the fix_bug function
            time.sleep(1)  # Sleep to simulate debugging delay
        else:
            print("Code ran successfully, no bugs found.")
            break  # Exit loop if no errors

if __name__ == "__main__":
    main()
