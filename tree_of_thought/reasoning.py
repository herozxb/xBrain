import ollama
import sys

# Safety check for the library conflict
if not hasattr(ollama, 'chat'):
    print("ERROR: Still detecting local 'ollama.py'. Rename your file and delete __pycache__.")
    sys.exit(1)

MODEL = "deepseek-coder-v2:latest"

def simulate_tree_of_thought():
    question = "What is the area of a triangle with base 5 and height 5?"
    print(f"\n[SYSTEM] Question: {question}")
    
    branches = []
    
    # 1. GENERATE 3 BRANCHES (The Tree)
    for i in range(1, 4):
        print(f"[THINKING] Exploring Branch {i}...")
        resp = ollama.chat(model=MODEL, messages=[
            {'role': 'user', 'content': f"Solve this math problem. Work step-by-step: {question}"}
        ])
        thought = resp['message']['content']
        branches.append(thought)

    # 2. VERIFY & SCORE (The Monologue)
    scored_branches = []
    for i, thought in enumerate(branches, 1):
        print(f"[VERIFYING] Scoring Branch {i}...")
        verify_resp = ollama.chat(model=MODEL, messages=[
            {'role': 'user', 'content': f"Critically evaluate this solution: '{thought}'. Is the math correct for a TRIANGLE? Score it from 0 to 100. Output ONLY the number."}
        ])
        
        # Extract digits to get the score
        score_text = verify_resp['message']['content']
        score = int(''.join(filter(str.isdigit, score_text)) or 0)
        scored_branches.append((score, thought))

    # 3. SELECT (The Best Path)
    # Sort by score descending and take the top one
    scored_branches.sort(key=lambda x: x[0], reverse=True)
    best_score, best_solution = scored_branches[0]

    print("\n" + "="*40)
    print(f"WINNING BRANCH SCORE: {best_score}/100")
    print("-" * 40)
    print(f"FINAL ANSWER:\n{best_solution}")

if __name__ == "__main__":
    simulate_tree_of_thought()

