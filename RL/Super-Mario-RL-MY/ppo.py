import pickle
import random
import time
from collections import deque

import gym_super_mario_bros
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from gym_super_mario_bros.actions import COMPLEX_MOVEMENT
from nes_py.wrappers import JoypadSpace

from wrappers import *
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QTimer


def get_enemy_info(env):
    ram = env.unwrapped.ram
    mario_level_x = ram[0x6D] * 256 + ram[0x86]
    mario_x = ram[0x3AD]
    mario_y = ram[0x3B8]
    x_start = mario_level_x - mario_x

    enemies = []
    for i in range(5):
        if ram[0x0F + i] == 1:
            enemy_x = ram[0x6E + i] * 256 + ram[0x87 + i] - x_start
            enemy_y = ram[0xCF + i]
            enemies.append((enemy_x, enemy_y))

    return mario_x, mario_y, enemies


def should_jump(env):
    mario_x, mario_y, enemies = get_enemy_info(env)

    for enemy_x, enemy_y in enemies:
        y_diff = abs((mario_y + 16) - (enemy_y + 8))
        if y_diff < 32:
            x_diff = abs((mario_x) - (enemy_x))
            if 0 < x_diff <= 32:
                return True
    return False


def get_rendered_screen(env):
    ram = env.unwrapped.ram

    mario_level_x = ram[0x6D] * 256 + ram[0x86]
    mario_x = ram[0x3AD]
    mario_y = ram[0x3B8] + 16
    x_start = mario_level_x - mario_x

    def tile_loc_to_ram_address(x, y):
        page = x // 16
        x_loc = x % 16
        y_loc = page * 13 + y
        return 0x500 + x_loc + y_loc * 16

    screen_start = int(round(x_start / 16))

    screen = np.zeros((13, 16))

    for i in range(16):
        for j in range(13):
            x_loc = (screen_start + i) % 32
            y_loc = j
            address = tile_loc_to_ram_address(x_loc, y_loc)
            if ram[address] != 0:
                screen[j, i] = 1

    mario_col = (mario_x + 8) // 16
    mario_row = (mario_y - 32) // 16
    if 0 <= mario_row < 13 and 0 <= mario_col < 16:
        screen[mario_row, mario_col] = 2

    for i in range(5):
        if ram[0x0F + i] == 1:
            enemy_x = ram[0x6E + i] * 256 + ram[0x87 + i] - x_start
            enemy_y = ram[0xCF + i]
            ex = (enemy_x + 8) // 16
            ey = (enemy_y + 8 - 32) // 16
            if 0 <= ey < 13 and 0 <= ex < 16:
                screen[ey, ex] = -1

    return screen


class FrameStack:
    def __init__(self, n_frame):
        self.n_frame = n_frame
        self.frames = None

    def get_state(self, screen):
        if not type(screen) == np.ndarray:
            screen = np.array(screen)

        if self.frames is None:
            self.frames = [screen] * self.n_frame
        else:
            self.frames.append(screen)
            self.frames.pop(0)

        return np.stack(self.frames, axis=0).flatten().reshape(1, -1)


frame_stack = None


def arrange_state(s):
    global frame_stack
    if frame_stack is None:
        frame_stack = FrameStack(4)
    return frame_stack.get_state(s)


class ActorCritic(nn.Module):
    def __init__(self, n_frame, n_action, device):
        super(ActorCritic, self).__init__()
        self.n_frame = n_frame
        input_size = n_frame * 16 * 13

        self.fc1 = nn.Linear(input_size, 5120)
        self.fc2 = nn.Linear(5120, 256)

        self.actor = nn.Linear(256, n_action)
        self.critic = nn.Linear(256, 1)

        self.device = device

        self.fc1.apply(self._init_weights)
        self.fc2.apply(self._init_weights)
        self.actor.apply(self._init_weights)
        self.critic.apply(self._init_weights)

    def _init_weights(self, m):
        if type(m) == nn.Linear:
            torch.nn.init.xavier_uniform_(m.weight)
            if m.bias is not None:
                m.bias.data.fill_(0.01)

    def forward(self, x):
        if type(x) != torch.Tensor:
            x = torch.FloatTensor(x).to(self.device)
        x = x.view(-1, self.n_frame * 16 * 13)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))

        policy = F.softmax(self.actor(x), dim=-1)
        value = self.critic(x)

        return policy, value

    def get_action(self, x):
        policy, value = self.forward(x)
        dist = torch.distributions.Categorical(policy)
        action = dist.sample()
        log_prob = dist.log_prob(action)
        return action.item(), log_prob, value, policy


class RolloutBuffer:
    def __init__(self):
        self.states = []
        self.actions = []
        self.log_probs = []
        self.rewards = []
        self.dones = []
        self.values = []

    def add(self, state, action, log_prob, reward, done, value):
        self.states.append(state)
        self.actions.append(action)
        self.log_probs.append(log_prob)
        self.rewards.append(reward)
        self.dones.append(done)
        self.values.append(value)

    def get(self, device="cpu"):
        states = torch.FloatTensor(np.array(self.states))
        actions = torch.tensor(self.actions)
        log_probs = torch.stack(self.log_probs)
        rewards = torch.tensor(self.rewards)
        dones = torch.tensor([1 - d for d in self.dones])
        values = torch.stack(self.values)

        return states, actions, log_probs, rewards, dones, values

    def clear(self):
        self.states = []
        self.actions = []
        self.log_probs = []
        self.rewards = []
        self.dones = []
        self.values = []


def compute_returns(rewards, dones, values, gamma=0.99, gae_lambda=0.95):
    returns = []
    gae = 0
    next_value = 0.0

    for t in reversed(range(len(rewards))):
        reward = (
            rewards[t].item() if isinstance(rewards[t], torch.Tensor) else rewards[t]
        )
        done = dones[t].item() if isinstance(dones[t], torch.Tensor) else dones[t]
        value = values[t].item() if isinstance(values[t], torch.Tensor) else values[t]

        delta = reward + gamma * next_value * done - value
        gae = delta + gamma * gae_lambda * done * gae
        returns.insert(0, gae + value)
        next_value = value

    return torch.tensor(returns, dtype=torch.float32)


def ppo_update(policy, optimizer, buffer, clip_eps=0.2, gamma=0.99, gae_lambda=0.95):
    device = policy.device
    states, actions, old_log_probs, rewards, dones, values = buffer.get(device)

    returns = compute_returns(rewards, dones, values, gamma, gae_lambda).to(device)
    advantages = (returns - values.to(device)).detach()

    old_log_probs = old_log_probs.detach()
    values = values.detach()
    returns = returns.detach()
    states = states.to(device)
    actions = actions.to(device)

    for _ in range(4):
        policy_opt, value = policy(states)

        dist = torch.distributions.Categorical(policy_opt)
        new_log_probs = dist.log_prob(actions)
        entropy = dist.entropy().mean()

        ratio = torch.exp(new_log_probs - old_log_probs)

        surr1 = ratio * advantages
        surr2 = torch.clamp(ratio, 1 - clip_eps, 1 + clip_eps) * advantages

        actor_loss = -torch.min(surr1, surr2).mean()
        critic_loss = F.mse_loss(value.squeeze(), returns)

        loss = actor_loss + 0.5 * critic_loss - 0.01 * entropy

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(policy.parameters(), 0.5)
        optimizer.step()

    buffer.clear()


class Visualizer(QtWidgets.QWidget):
    def __init__(self, parent, size):
        super().__init__(parent)
        self.size = size
        self.screen = None

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
        painter.drawRect(0, 0, self.size[0], self.size[1])

        if self.screen is not None:
            tile_size = 16
            for row in range(13):
                for col in range(16):
                    val = self.screen[row, col]
                    x_start = 5 + col * tile_size
                    y_start = 5 + row * tile_size

                    if val == 0:
                        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
                    elif val == 1:
                        painter.setBrush(QBrush(QColor(139, 69, 19), Qt.SolidPattern))
                    elif val == 2:
                        painter.setBrush(QBrush(QColor(0, 0, 255), Qt.SolidPattern))
                    elif val == -1:
                        painter.setBrush(QBrush(QColor(255, 0, 0), Qt.SolidPattern))

                    painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
                    painter.drawRect(x_start, y_start, tile_size, tile_size)

        painter.end()

    def _update(self, screen):
        self.screen = screen
        self.update()


class GameWindow(QtWidgets.QMainWindow):
    def __init__(self, env, policy, device):
        super().__init__()
        self.setWindowTitle("Super Mario Bros AI - PPO")
        self.setGeometry(100, 100, 700, 400)

        self.env = env
        self.policy = policy
        self.device = device

        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.env.reset()

        self.viz_window = Visualizer(self.centralWidget, (500, 300))
        self.viz_window.setGeometry(0, 0, 500, 300)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.viz_window)

        self.label = QtWidgets.QLabel("Training PPO...")
        layout.addWidget(self.label)
        self.centralWidget.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(100)

        global frame_stack
        frame_stack = FrameStack(4)

    def update_game(self):
        global frame_stack

        screen = get_rendered_screen(self.env)
        self.viz_window._update(screen)
        self.env.unwrapped.render()


def main(env, policy, optimizer, device, qt_app=None, game_window=None):
    global frame_stack

    update_interval = 128
    max_steps = 2048
    clip_eps = 0.2
    gamma = 0.99
    gae_lambda = 0.95

    buffer = RolloutBuffer()
    print_interval = 10
    score_lst = []
    total_score = 0.0
    episode_count = 0
    start_time = time.perf_counter()
    best_score = -float("inf")

    for k in range(1000000):
        frame_stack = FrameStack(4)
        env.reset()
        screen = get_rendered_screen(env)
        s = arrange_state(screen)
        done = False
        episode_score = 0
        step_count = 0

        while not done:
            if should_jump(env):
                action = 5
            elif np.random.rand() < 0.002:
                action = env.action_space.sample()
            else:
                action, log_prob, value, _ = policy.get_action(s)
                action = action
                log_prob = log_prob.unsqueeze(0)
                value = value.squeeze()

            s_prime, r, done, _ = env.step(action)
            screen = get_rendered_screen(env)
            s_prime = arrange_state(screen)

            r = np.sign(r) * (np.sqrt(abs(r) + 1) - 1) + 0.001 * r
            episode_score += r
            total_score += r

            buffer.add(s, action, log_prob, r, done, value)
            s = s_prime
            step_count += 1

            if step_count >= max_steps:
                break

            if game_window is not None:
                game_window.viz_window._update(screen)

            if qt_app is not None:
                qt_app.processEvents()

        episode_count += 1

        if buffer.states:
            ppo_update(policy, optimizer, buffer, clip_eps, gamma, gae_lambda)

        if episode_score > best_score:
            best_score = episode_score
            torch.save(policy.state_dict(), "mario_ppo.pth")

        if k % print_interval == 0:
            time_spent = time.perf_counter() - start_time
            print(
                "%s |Episode : %d | score : %.1f | best : %.1f | time : %.1f"
                % (device, k, episode_score, best_score, time_spent)
            )

            score_lst.append(episode_score)
            total_score = 0
            pickle.dump(score_lst, open("score_ppo.p", "wb"))


if __name__ == "__main__":
    n_frame = 4
    env = gym_super_mario_bros.make("SuperMarioBros-v0", target=(1, 2))
    env = JoypadSpace(env, COMPLEX_MOVEMENT)
    env = wrap_mario(env)
    device = "cpu"

    torch.set_num_threads(torch.get_num_threads())
    print(f"Using {torch.get_num_threads()} threads")

    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"

    policy = ActorCritic(n_frame, env.action_space.n, device).to(device)

    policy_model_path = "mario_ppo.pth"
    try:
        policy.load_state_dict(torch.load(policy_model_path, map_location=device))
        print(f"Loaded PPO policy from {policy_model_path}")
    except FileNotFoundError:
        print("No saved model, using random initialization")

    optimizer = optim.Adam(policy.parameters(), lr=0.0001)
    print(device)

    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = GameWindow(env, policy, device)
    window.show()

    main(env, policy, optimizer, device, app, window)

    sys.exit(app.exec_())
