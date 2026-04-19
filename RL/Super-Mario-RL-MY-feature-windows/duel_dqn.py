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
from gym_super_mario_bros.actions import SIMPLE_MOVEMENT
from nes_py.wrappers import JoypadSpace

from wrappers import *
from PyQt5 import QtGui, QtWidgets
from PyQt5.QtGui import QPainter, QBrush, QPen, QColor
from PyQt5.QtCore import Qt, QTimer


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


class replay_memory(object):
    def __init__(self, N):
        self.memory = deque(maxlen=N)

    def push(self, transition):
        self.memory.append(transition)

    def sample(self, n):
        return random.sample(self.memory, n)

    def __len__(self):
        return len(self.memory)


class best_memory:
    def __init__(self, top_k=100):
        self.top_k = top_k
        self.episodes = []
        self.best_scores = []

    def push(self, episode_score, transitions):
        self.episodes.append((episode_score, transitions))
        self.episodes.sort(key=lambda x: x[0], reverse=True)
        if len(self.episodes) > self.top_k:
            self.episodes = self.episodes[: self.top_k]

    def get_all(self):
        result = []
        for score, transitions in self.episodes:
            result.extend(transitions)
        return result

    def __len__(self):
        return len(self.episodes)

    def num_transitions(self):
        return sum(len(t) for _, t in self.episodes)

    def sample(self, n):
        all_transitions = self.get_all()
        if len(all_transitions) == 0:
            return []
        return random.sample(all_transitions, min(n, len(all_transitions)))


class model(nn.Module):
    def __init__(self, n_frame, n_action, device):
        super(model, self).__init__()
        self.n_frame = n_frame
        self.n_action = n_action
        self.device = device

        self.conv1 = nn.Conv2d(n_frame, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)

        conv_out_size = 128 * 13 * 16

        self.fc1 = nn.Linear(conv_out_size, 256)
        self.fc2 = nn.Linear(256, 128)

        self.fc_v = nn.Linear(128, 64)
        self.v = nn.Linear(64, 1)

        self.fc_a = nn.Linear(128, 64)
        self.a = nn.Linear(64, n_action)

        self.conv1.apply(init_weights)
        self.conv2.apply(init_weights)
        self.conv3.apply(init_weights)
        self.fc1.apply(init_weights)
        self.fc2.apply(init_weights)
        self.fc_v.apply(init_weights)
        self.fc_a.apply(init_weights)
        self.v.apply(init_weights)
        self.a.apply(init_weights)

    def forward(self, x):
        if type(x) != torch.Tensor:
            x = torch.FloatTensor(x).to(self.device)

        x = x.view(-1, self.n_frame, 13, 16)

        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        x = torch.relu(self.conv3(x))

        x = x.view(x.size(0), -1)

        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))

        v = torch.relu(self.fc_v(x))
        v = self.v(v)

        a = torch.relu(self.fc_a(x))
        a = self.a(a)

        q = v + (a - a.mean(dim=-1, keepdim=True))

        return q

    def get_conv1_features(self, x):
        if type(x) != torch.Tensor:
            x = torch.FloatTensor(x).to(self.device)
        x = x.view(-1, self.n_frame, 13, 16)
        return torch.relu(self.conv1(x))

    def get_conv2_features(self, x):
        if type(x) != torch.Tensor:
            x = torch.FloatTensor(x).to(self.device)
        x = x.view(-1, self.n_frame, 13, 16)
        x = torch.relu(self.conv1(x))
        return torch.relu(self.conv2(x))

    def get_conv3_features(self, x):
        if type(x) != torch.Tensor:
            x = torch.FloatTensor(x).to(self.device)
        x = x.view(-1, self.n_frame, 13, 16)
        x = torch.relu(self.conv1(x))
        x = torch.relu(self.conv2(x))
        return torch.relu(self.conv3(x))


def init_weights(m):
    if type(m) == nn.Linear:
        torch.nn.init.xavier_uniform_(m.weight)
        if m.bias is not None:
            m.bias.data.fill_(0.01)


def train(q, q_target, memory, batch_size, gamma, optimizer, device):
    s, r, a, s_prime, done = list(map(list, zip(*memory.sample(batch_size))))

    s = np.array(s).squeeze()
    s_prime = np.array(s_prime).squeeze()
    a_max = q(s_prime).max(1)[1].unsqueeze(-1)

    r = torch.FloatTensor(r).unsqueeze(-1).to(device)
    done = torch.FloatTensor(done).unsqueeze(-1).to(device)

    with torch.no_grad():
        y = r + gamma * q_target(s_prime).gather(1, a_max) * done

    a = torch.tensor(a).unsqueeze(-1).to(device)
    q_value = torch.gather(q(s), dim=1, index=a.view(-1, 1).long())

    loss = F.smooth_l1_loss(q_value, y).mean()

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return loss


def copy_weights(q, q_target):
    q_dict = q.state_dict()
    q_target.load_state_dict(q_dict)


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


class FeatureVisualizer(QtWidgets.QWidget):
    def __init__(self, parent, size):
        super().__init__(parent)
        self.size = size
        self.features = None
        self.channel = 0

    def paintEvent(self, event):
        painter = QPainter()
        if not painter.begin(self):
            return
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
        painter.drawRect(0, 0, self.size[0], self.size[1])

        if self.features is not None:
            feat = self.features[0, self.channel].cpu().detach().numpy()
            feat = (feat - feat.min()) / (feat.max() - feat.min() + 1e-8)
            tile_size = self.size[0] // 16
            for row in range(13):
                for col in range(16):
                    val = int(feat[row, col] * 255)
                    painter.setBrush(QBrush(QColor(val, val, val), Qt.SolidPattern))
                    painter.drawRect(
                        col * tile_size, row * tile_size, tile_size, tile_size
                    )
        painter.end()

    def _update(self, features, channel=0):
        self.features = features
        self.channel = channel
        self.update()


class FeatureWindow(QtWidgets.QMainWindow):
    def __init__(self, q, device):
        super().__init__()
        self.setWindowTitle("Feature Maps")
        self.setGeometry(300, 100, 300, 350)
        self.q = q
        self.device = device

        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        layout = QtWidgets.QVBoxLayout()
        self.centralWidget.setLayout(layout)

        self.feature_viz = FeatureVisualizer(self.centralWidget, (256, 208))
        layout.addWidget(self.feature_viz)

        self.channel_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.channel_slider.setMinimum(0)
        self.channel_slider.setMaximum(31)
        layout.addWidget(self.channel_slider)

        self.channel_label = QtWidgets.QLabel("Channel: 0")
        layout.addWidget(self.channel_label)

        self.conv_selector = QtWidgets.QComboBox()
        self.conv_selector.addItems(["conv1 (32)", "conv2 (64)", "conv3 (128)"])
        layout.addWidget(self.conv_selector)

        self.layer = 0
        self.channel = 0
        self.conv_selector.currentIndexChanged.connect(self.on_layer_change)
        self.channel_slider.valueChanged.connect(self.on_channel_change)

    def on_layer_change(self):
        self.layer = self.conv_selector.currentIndex()
        if self.layer == 0:
            self.channel_slider.setMaximum(31)
        elif self.layer == 1:
            self.channel_slider.setMaximum(63)
        else:
            self.channel_slider.setMaximum(127)

    def on_channel_change(self):
        self.channel = self.channel_slider.value()
        self.channel_label.setText(f"Channel: {self.channel}")

    def set_state(self, state):
        self.last_state = state
        if self.layer == 0:
            features = self.q.get_conv1_features(state)
        elif self.layer == 1:
            features = self.q.get_conv2_features(state)
        else:
            features = self.q.get_conv3_features(state)
        self.feature_viz._update(features, self.channel)


class KernelVisualizerWindow(QtWidgets.QWidget):
    def __init__(self, parent, size):
        super().__init__(parent)
        self.size = size
        self.kernels = None
        self.channel = 0

    def paintEvent(self, event):
        painter = QPainter()
        if not painter.begin(self):
            return
        painter.setPen(QPen(Qt.NoPen))
        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
        painter.drawRect(0, 0, self.size[0], self.size[1])

        if self.kernels is not None:
            k = self.kernels
            if self.channel < k.shape[0]:
                kernel = k[self.channel]
                cell = min(self.size[0], self.size[1]) // 3
                x0 = (self.size[0] - cell * 3) // 2
                y0 = (self.size[1] - cell * 3) // 2
                for di in range(3):
                    for dj in range(3):
                        val = kernel[:, di, dj].mean().item()
                        v = int(abs(val) * 255)
                        painter.setBrush(QBrush(QColor(v, v, v), Qt.SolidPattern))
                        painter.drawRect(x0 + dj * cell, y0 + di * cell, cell, cell)
        painter.end()

    def _update(self, kernels, channel=0):
        self.kernels = kernels
        self.channel = channel
        self.update()


class KernelWindow(QtWidgets.QMainWindow):
    def __init__(self, q, device):
        super().__init__()
        self.setWindowTitle("Kernel Weights")
        self.setGeometry(600, 100, 300, 350)
        self.q = q
        self.device = device

        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)
        layout = QtWidgets.QVBoxLayout()
        self.centralWidget.setLayout(layout)

        self.kernel_viz = KernelVisualizerWindow(self.centralWidget, (256, 256))
        layout.addWidget(self.kernel_viz)

        self.channel_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.channel_slider.setMinimum(0)
        self.channel_slider.setMaximum(31)
        layout.addWidget(self.channel_slider)

        self.channel_label = QtWidgets.QLabel("Kernel: 0")
        layout.addWidget(self.channel_label)

        self.conv_selector = QtWidgets.QComboBox()
        self.conv_selector.addItems(["conv1 (32)", "conv2 (64)", "conv3 (128)"])
        layout.addWidget(self.conv_selector)

        self.layer = 0
        self.channel = 0
        self.conv_selector.currentIndexChanged.connect(self.on_layer_change)
        self.channel_slider.valueChanged.connect(self.on_channel_change)

    def on_layer_change(self):
        self.layer = self.conv_selector.currentIndex()
        if self.layer == 0:
            self.channel_slider.setMaximum(31)
            kernels = self.q.conv1.weight.data
        elif self.layer == 1:
            self.channel_slider.setMaximum(63)
            kernels = self.q.conv2.weight.data
        else:
            self.channel_slider.setMaximum(127)
            kernels = self.q.conv3.weight.data
        self.channel_label.setText(f"Kernel: {self.channel}")
        self.kernel_viz._update(kernels, self.channel)

    def on_channel_change(self):
        self.channel = self.channel_slider.value()
        self.channel_label.setText(f"Kernel: {self.channel}")
        if self.layer == 0:
            kernels = self.q.conv1.weight.data
        elif self.layer == 1:
            kernels = self.q.conv2.weight.data
        else:
            kernels = self.q.conv3.weight.data
        self.kernel_viz._update(kernels, self.channel)

    def update_kernels(self):
        if self.layer == 0:
            kernels = self.q.conv1.weight.data
        elif self.layer == 1:
            kernels = self.q.conv2.weight.data
        else:
            kernels = self.q.conv3.weight.data
        self.kernel_viz._update(kernels, self.channel)


class GameWindow(QtWidgets.QMainWindow):
    def __init__(self, env, q, device):
        super().__init__()
        self.setWindowTitle("Super Mario Bros AI - DQN")
        self.setGeometry(100, 100, 700, 400)

        self.env = env
        self.q = q
        self.device = device

        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.env.reset()

        self.viz_window = Visualizer(self.centralWidget, (500, 300))
        self.viz_window.setGeometry(0, 0, 500, 300)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.viz_window)

        self.label = QtWidgets.QLabel("Training...")
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


def main(
    env,
    q,
    q_target,
    optimizer,
    device,
    qt_app=None,
    game_window=None,
    feature_window=None,
    kernel_window=None,
):
    global frame_stack

    t = 0
    gamma = 0.99
    batch_size = 256

    N = 50000
    eps = 0.002
    memory = replay_memory(N)
    best_mem = best_memory(top_k=50)
    print_interval = 10

    score_lst = []
    total_score = 0.0
    loss = 0.0
    start_time = time.perf_counter()
    best_score = -float("inf")

    for k in range(1000000):
        frame_stack = FrameStack(4)
        env.reset()
        screen = get_rendered_screen(env)
        s = arrange_state(screen)
        done = False
        episode_transitions = []
        episode_score = 0
        while not done:
            if eps > np.random.rand():
                a = env.action_space.sample()
            else:
                if device == "cpu":
                    q_values = q(s).detach().numpy()[0]
                else:
                    q_values = q(s).cpu().detach().numpy()[0]

                a = np.argmax(q_values)

            s_prime, r, done, _ = env.step(a)
            screen = get_rendered_screen(env)
            s_prime = arrange_state(screen)
            total_score += r
            episode_score += r

            # print(f"Episode score: {episode_score}, Best mem transitions: {best_mem.num_transitions()}")

            r = np.sign(r) * (np.sqrt(abs(r) + 1) - 1) + 0.001 * r

            memory.push((s, float(r), int(a), s_prime, int(1 - done)))
            episode_transitions.append((s, float(r), int(a), s_prime, int(1 - done)))
            s = s_prime
            stage = env.unwrapped._stage

            if len(memory) > 2000:
                if len(best_mem) > 0 and best_mem.num_transitions() >= batch_size // 4:
                    best_batch = best_mem.sample(batch_size // 256 * 255)
                    normal_batch = memory.sample(batch_size // 256 * 1)
                    combined = normal_batch + list(best_batch)
                    random.shuffle(combined)
                    fake_mem = type(
                        "FakeMemory", (), {"sample": lambda self, n: combined}
                    )()
                    loss += train(
                        q, q_target, fake_mem, batch_size, gamma, optimizer, device
                    )
                else:
                    loss += train(
                        q, q_target, memory, batch_size, gamma, optimizer, device
                    )
                t += 1

            if game_window is not None:
                game_window.viz_window._update(screen)
                game_window.label.setText(f"Step: {t}, Loss: {loss:.2f}")

            if feature_window is not None:
                feature_window.set_state(s)

            if kernel_window is not None:
                kernel_window.update_kernels()

            if qt_app is not None:
                qt_app.processEvents()

        if episode_score > 700:
            best_mem.push(episode_score, episode_transitions)

        # print(f"Episode score: {episode_score}, Best mem transitions: {best_mem.num_transitions()}")
        avg_score = total_score / print_interval

        if avg_score > best_score:
            best_score = avg_score
            if best_score > 1000:
                best_score = best_score - 0
            copy_weights(q, q_target)
            torch.save(q.state_dict(), "mario_q.pth")
            torch.save(q_target.state_dict(), "mario_q_target.pth")

        if k % print_interval == 0:
            if best_score - avg_score > 300:
                print("===restore best model===")
                copy_weights(q_target, q)
            time_spent, start_time = (
                time.perf_counter() - start_time,
                time.perf_counter(),
            )

            print(
                "%s |Epoch : %d | score : %f  | best score : %f | loss : %.2f | stage : %d | time spent: %f"
                % (
                    device,
                    k,
                    total_score / print_interval,
                    best_score,
                    loss / print_interval,
                    stage,
                    time_spent,
                )
            )

            score_lst.append(total_score / print_interval)
            total_score = 0
            loss = 0.0
            pickle.dump(score_lst, open("score.p", "wb"))


if __name__ == "__main__":
    n_frame = 4
    env = gym_super_mario_bros.make("SuperMarioBros-v0", target=(1, 2))
    env = JoypadSpace(env, SIMPLE_MOVEMENT)
    env = wrap_mario(env)
    device = "cpu"

    torch.set_num_threads(torch.get_num_threads())
    print(f"Using {torch.get_num_threads()} threads")

    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    q = model(n_frame, env.action_space.n, device).to(device)
    q_target = model(n_frame, env.action_space.n, device).to(device)

    # 定义模型路径
    q_model_path = "mario_q.pth"
    q_target_model_path = "mario_q_target.pth"

    try:
        # 加载 Q 网络的参数
        q.load_state_dict(torch.load(q_model_path, map_location=device))
        print(f"成功加载 Q 网络参数从 {q_model_path}")
    except FileNotFoundError:
        print(f"警告: 未找到 {q_model_path}，Q 网络将使用随机初始化的参数")

    try:
        # 加载目标 Q 网络的参数
        q_target.load_state_dict(torch.load(q_target_model_path, map_location=device))
        print(f"成功加载目标 Q 网络参数从 {q_target_model_path}")
    except FileNotFoundError:
        print(f"警告: 未找到 {q_target_model_path}，目标 Q 网络将使用随机初始化的参数")
        # 如果目标网络没有预训练参数，可以初始化为与 Q 网络相同
        q_target.load_state_dict(q.state_dict())

    optimizer = optim.Adam(q.parameters(), lr=0.0001)
    print(device)

    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = GameWindow(env, q, device)
    window.show()

    feature_window = FeatureWindow(q, device)
    feature_window.show()

    kernel_window = KernelWindow(q, device)
    kernel_window.show()

    main(
        env, q, q_target, optimizer, device, app, window, feature_window, kernel_window
    )

    sys.exit(app.exec_())
