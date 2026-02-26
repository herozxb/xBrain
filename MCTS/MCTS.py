import math
import random

class MCTSNode:
    def __init__(self, state, parent=None):
        self.state = state  # The current 'thought' or 'answer'
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0  # Cumulative reward/score
        self.untried_actions = ["Logic A", "Logic B", "Logic C"] # Potential paths

    def uct_score(self, total_visits, exploration=1.41):
        """Upper Confidence Bound for Trees (UCT) formula."""
        if self.visits == 0: return float('inf')
        return (self.value / self.visits) + exploration * math.sqrt(math.log(total_visits) / self.visits)

def simulate_mcts(iterations=10):
    root = MCTSNode("Problem: Area of Triangle (b=5, h=5)")

    for _ in range(iterations):
        # 1. SELECTION: Pick most promising leaf node using UCT
        node = root
        while node.children and not node.untried_actions:
            node = max(node.children, key=lambda c: c.uct_score(node.visits))

        # 2. EXPANSION: If not terminal, create a new child
        if node.untried_actions:
            action = node.untried_actions.pop()
            new_node = MCTSNode(f"{node.state} -> {action}", parent=node)
            node.children.append(new_node)
            node = new_node

        # 3. SIMULATION (Rollout): Randomly 'finish' the thought
        # In a real LLM, this is where it finishes the sentence.
        simulated_reward = random.uniform(0, 100) # Simplified reward

        # 4. BACKPROPAGATION: Send the score back up the tree
        temp_node = node
        while temp_node:
            temp_node.visits += 1
            temp_node.value += simulated_reward
            temp_node = temp_node.parent

    # Pick the best 'first step' found
    best_child = max(root.children, key=lambda c: c.visits)
    return best_child.state

print(f"MCTS Recommended Path: {simulate_mcts()}")

