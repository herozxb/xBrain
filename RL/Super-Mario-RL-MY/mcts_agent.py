import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import math


def convert_to_model_input(screen):
    """Convert screen (13,16) to (832,) by repeating 4 times"""
    if not type(screen) == np.ndarray:
        screen = np.array(screen)
    return np.repeat(screen.flatten(), 4)


class MCTSNode:
    def __init__(
        self, state_original, state_model=None, parent=None, action=None, prior=0.0
    ):
        self.state_original = (
            state_original.copy() if state_original is not None else None
        )
        self.state_model = state_model
        self.parent = parent
        self.action = action
        self.children = {}
        self.n_visits = 0
        self.Q = 0.0
        self.prior = prior
        self.value_sum = 0.0

    def is_expanded(self):
        return len(self.children) > 0

    def select_child(self, c_puct=1.4):
        best_score = -float("inf")
        best_child = None
        for action, child in self.children.items():
            u = (
                c_puct
                * child.prior
                * math.sqrt(self.n_visits + 1)
                / (child.n_visits + 1)
            )
            score = child.Q + u
            if score > best_score:
                best_score = score
                best_child = child
        return best_child

    def expand(self, action_priors, next_states_model):
        for action, prior in action_priors.items():
            if action not in self.children:
                state_model = next_states_model.get(action)
                self.children[action] = MCTSNode(None, state_model, self, action, prior)

    def update(self, value):
        self.n_visits += 1
        self.value_sum += value
        self.Q = self.value_sum / self.n_visits


class AlphaGoMCTS:
    def __init__(self, model, device, n_simulations=50, c_puct=1.4, max_depth=10):
        self.model = model
        self.device = device
        self.n_simulations = n_simulations
        self.c_puct = c_puct
        self.max_depth = max_depth
        self.world_model = None

    def set_world_model(self, world_model):
        self.world_model = world_model

    def predict_next_state(self, state_model, action):
        if self.world_model is None:
            return None, False
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state_model).unsqueeze(0).to(self.device)
            action_tensor = torch.FloatTensor([action]).to(self.device)
            pred = self.world_model(state_tensor, action_tensor)
            pred_np = pred.cpu().numpy()[0]
            next_state = pred_np
            done = False
            return next_state, done

    def get_priors_and_next_states(self, state_original, state_model, valid_actions):
        next_states_model = {}
        priors = {}

        for action in valid_actions:
            next_s, done = self.predict_next_state(state_model, action)
            if done or next_s is None:
                next_states_model[action] = None
            else:
                next_states_model[action] = next_s

            if next_states_model[action] is not None:
                with torch.no_grad():
                    state_tensor = (
                        torch.FloatTensor(next_states_model[action])
                        .unsqueeze(0)
                        .to(self.device)
                    )
                    q_values = self.model(state_tensor).cpu().numpy()[0]
                priors[action] = math.exp(q_values.max() / 1.0)
            else:
                priors[action] = 0.0

        total = sum(priors.values()) + 1e-8
        for a in priors:
            priors[a] /= total
        return priors, next_states_model

        total = sum(priors.values()) + 1e-8
        for a in priors:
            priors[a] /= total
        return priors, next_states_original, next_states_model

    def evaluate(self, state_model):
        if state_model is None:
            return 0.0
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state_model).unsqueeze(0).to(self.device)
            q_values = self.model(state_tensor).cpu().numpy()[0]
        return np.max(q_values)

    def simulate(self, env):
        for _ in range(self.n_simulations):
            node = root = self.root
            path = [node]
            depth = 0

            while node.is_expanded() and depth < self.max_depth:
                node = node.select_child(self.c_puct)
                if node.state is None:
                    break
                path.append(node)
                depth += 1

            if not node.is_expanded() and node.state is not None:
                valid_actions = list(range(env.action_space.n))
                priors, next_states = self.get_priors_and_next_states(
                    node.state, env, valid_actions
                )
                node.expand(priors, next_states)

            value = self.evaluate(node.state)
            self.backup(path, value)

        return self.get_policy(root, list(range(env.action_space.n)))

    def search(self, state_model, valid_actions):
        state_model = state_model.reshape(4, 13, 16)
        self.root = MCTSNode(None, state_model)

        for _ in range(self.n_simulations):
            node = self.root
            path = [node]
            depth = 0

            while node.is_expanded() and depth < self.max_depth:
                node = node.select_child(self.c_puct)
                if node.state_model is None:
                    break
                path.append(node)
                depth += 1

            if not node.is_expanded() and node.state_model is not None:
                priors, next_states_model = self.get_priors_and_next_states(
                    None, node.state_model, valid_actions
                )
                node.expand(priors, next_states_model)

            value = self.evaluate(node.state_model)
            self.backup(path, value)

        return self.get_policy(self.root, valid_actions), self.root

    def backup(self, path, value):
        for node in reversed(path):
            node.update(value)

    def get_policy(self, root, valid_actions):
        probs = np.zeros(len(valid_actions))
        for i, a in enumerate(valid_actions):
            if a in root.children:
                probs[i] = root.children[a].n_visits

        if probs.sum() > 0:
            probs = probs / probs.sum()
        else:
            probs = np.ones(len(valid_actions)) / len(valid_actions)
        return {a: p for a, p in zip(valid_actions, probs)}


class AlphaGoMCTSAgent:
    def __init__(
        self, model, device, n_simulations=25, c_puct=1.4, max_depth=10, temperature=1.0
    ):
        self.model = model
        self.device = device
        self.mcts = AlphaGoMCTS(model, device, n_simulations, c_puct, max_depth)
        self.temperature = temperature
        self.valid_actions = None

    def set_valid_actions(self, valid_actions):
        self.valid_actions = valid_actions

    def set_state_converter(self, converter_fn):
        self.mcts.set_state_converter(converter_fn)

    def get_action(self, state, env, temperature=None):
        if temperature is None:
            temperature = self.temperature

        policy, _ = self.mcts.search(state, env, self.valid_actions)

        counts = np.array([policy.get(a, 0) for a in self.valid_actions])
        if temperature > 0:
            counts = counts ** (1.0 / temperature)
        probs = counts / (counts.sum() + 1e-8)

        return np.random.choice(self.valid_actions, p=probs)
