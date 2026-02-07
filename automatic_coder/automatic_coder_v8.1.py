import subprocess
import time
import ollama
import re
import fileinput



# Step 1: Generate Python code and save to a file
def generate_python_code():
    code = """
# Use DeepSeek Coder V2 to suggest fixes based on the error output
def sample_function():
                    a
                    b
                                        c
    d
e
        f1111
        prompt = " write hello world"
        # Sending code to DeepSeek Coder V2
        response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
        suggested_code = response['message']['content']
    """
    with open("python_code.py", "w") as f:
        f.write(code)

def overwrite_python_code(code):
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


def fix_bug(error_output):
    print("# 2.1 Analyzing error for fix...")
    
    # Extract line number from typical Python traceback
    match = re.search(r'line (\d+)', error_output)
    if not match:
        print("# Error: Could not parse line number.")
        return

    target_line_no = int(match.group(1))
    
    # Logic to fix the reporting discrepancy:
    # If the error is 'expected an indented block', the real issue is usually the line ABOVE.
    if "IndentationError: expected an indented block" in error_output:
        print(f"# 2.2 Detected IndentationError on line {target_line_no}. Adjusting target to line {target_line_no - 1}.")
        target_line_no -= 1

    fix_suggestion = get_deepseek_fix(error_output).strip()

    if fix_suggestion:
        print(f"# 2.3 ================= Suggested fix for line [{target_line_no}]: ================= \n{fix_suggestion}")
        
        # Use fileinput for in-place editing
        with fileinput.input("python_code.py", inplace=True) as file:
            for line in file:
                if file.lineno() == target_line_no:
                    # ---- DELETE original line by NOT printing it ----

                    if 1:
                        # capture original indentation
                        indent = line[:len(line) - len(line.lstrip())]
                    else:
                        indent = ""

                    # ---- INSERT new code ----
                    for new_line in fix_suggestion.splitlines():
                        print(f"{indent}{new_line}")
                else:
                    print(line, end='')

def get_python_code(LLM_code):

    if "```python" in LLM_code and "```" in LLM_code:
        # Extract code between ```python and closing ```
        start = LLM_code.find("```python") + len("```python")
        end = LLM_code.find("```", start)
        code = LLM_code[start:end].strip()
        return code
    else:
        # If no ```python``` block is found, return the full response
        return LLM_code


# Initialize DeepSeek Coder V2 model
def get_deepseek_fix(error_output):
    # Use DeepSeek Coder V2 to suggest fixes based on the error output
    model_name = "deepseek-coder-v2:latest"  # Replace with your DeepSeek model name
    prompt = f"""Fix the following Python code error: {error_output}. 
    Suggest a solution for the issue.
    CODE QUALITY:
    - No explanatory text or comments
    - Production-ready code
    """

    try:
        print("# 3.1 Fixing the bug by the LLM of deepseek-coder-v2")
        # Sending the error message to DeepSeek Coder V2 for suggestions
        response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
        # Extracting the Python code from the response and ensuring it's wrapped in triple backticks with 'python'
        suggested_code = response['message']['content']

        return get_python_code(suggested_code)

    except Exception as e:
        print(f"Error using DeepSeek Coder V2: {e}")
        return None

def deepseek_fix_whole_code( stderr ):
    try:
        # Read the entire content of python_code.py
        with open("python_code.py", "r") as file:
            whole_code = file.read()

        print(f"Original code:\n{whole_code}")
        print("=========================deepseek_fix_whole_code=============================")
        
        # Send the entire code to DeepSeek Coder V2 for a fix suggestion
        model_name = "deepseek-coder-v2:latest"
        prompt = f"""Fix the following Python code:\n\n
            {whole_code}\n\nProvide the fixed version of the code. 
            the error message is {stderr}
            CODE QUALITY:
                - No explanatory text or comments
                - Production-ready code
            """
        
        # Sending code to DeepSeek Coder V2
        response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
        suggested_code = response['message']['content']
        
        print(f"Suggested fixed code from DeepSeek Coder V2:\n{suggested_code}")

        overwrite_python_code(get_python_code(suggested_code))
    
    except Exception as e:
        print(f"Error fixing the whole code with DeepSeek Coder V2: {e}")


# Main loop to generate, run, debug, fix, and repeat
def main():
    # Step 1: Generate code
    generate_python_code()  
    counter = 0
    while True:

        # Step 2: Run the code
        result = run_python_file()  

        if result and result.stderr:
            # Step 3: If there's an error, capture the error and fix the bug
            print(f"Bug detected, error message: {result.stderr}")
            # Pass the error message to the fix_bug function
            fix_bug(result.stderr)  
            # Sleep to simulate debugging delay
            time.sleep(1)  
        else:
            print("Code ran successfully, no bugs found.")
            # Exit loop if no errors
            break  

        counter+=1
        if counter > 5 and result.stderr :
            deepseek_fix_whole_code( result.stderr )
            counter=0

if __name__ == "__main__":
    main()
