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

class WorldModel(nn.Module):
    def __init__(self, n_frame, n_action, device):
        super(WorldModel, self).__init__()
        self.n_frame = n_frame
        self.n_action = n_action
        self.device = device

        self.hidden_dim = 128
        self.num_heads = 4
        self.num_layers = 2

        self.cell_embed = nn.Linear(1, self.hidden_dim)
        self.action_embed = nn.Linear(n_action, self.hidden_dim)

        max_seq = n_frame * 13 * 16
        self.pos_embed = nn.Parameter(torch.randn(1, max_seq, self.hidden_dim) * 0.02)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.hidden_dim,
            nhead=self.num_heads,
            dim_feedforward=self.hidden_dim * 4,
            dropout=0.1,
            batch_first=True,
        )
        self.transformer = nn.TransformerEncoder(
            encoder_layer, num_layers=self.num_layers
        )

        self.output_embed = nn.Linear(self.hidden_dim, 1)

    def forward(self, state, action):
        if type(state) != torch.Tensor:
            state = torch.FloatTensor(state).to(self.device)
        if type(action) != torch.Tensor:
            action = torch.FloatTensor([action]).to(self.device)

        if state.dim() == 2:
            state = state.unsqueeze(0)
        if action.dim() == 0:
            action = action.unsqueeze(0)

        batch_size = state.size(0)
        seq_len = self.n_frame * 13 * 16

        cell_val = state.view(batch_size, seq_len, 1)
        cell_emb = self.cell_embed(cell_val)

        action_one_hot = torch.zeros(batch_size, self.n_action).to(self.device)
        a_idx = action.long().clamp(0, self.n_action - 1)
        action_one_hot.scatter_(1, a_idx.view(-1, 1), 1.0)
        action_emb = (
            self.action_embed(action_one_hot).unsqueeze(1).expand(-1, seq_len, -1)
        )

        x = cell_emb + action_emb

        pos_emb = self.pos_embed[:, :seq_len, :].to(self.device)
        x = x + pos_emb

        encoded = self.transformer(x)

        pred_cell = self.output_embed(encoded)
        pred_cell = pred_cell.view(batch_size, seq_len, 1)

        return pred_cell.view(batch_size, self.n_frame, 13, 16)


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

    def forward(self, x):
        if type(x) != torch.Tensor:
            x = torch.FloatTensor(x).to(self.device)

        x = x.view(-1, self.n_frame, 13, 16)
        x = torch.relu(self.conv1(x))
        conv1_out = x
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
        x = torch.relu(self.conv1(x))
        return x


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


def train_world_model(world_model, memory, batch_size, optimizer, device):
    if len(memory) < batch_size:
        return 0.0

    transitions = memory.sample(batch_size)
    s, r, a, s_prime, done = list(map(list, zip(*transitions)))

    s = torch.FloatTensor(np.array(s)).to(device)
    s_prime = torch.FloatTensor(np.array(s_prime)).to(device)
    a = torch.tensor(a).float().to(device)

    pred = world_model(s, a)
    pred = pred.view(pred.size(0), -1)

    loss = F.mse_loss(pred, s_prime)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return loss.item()


def copy_weights(q, q_target):
    q_dict = q.state_dict()
    q_target.load_state_dict(q_dict)


class ScreenVisualizer(QtWidgets.QWidget):
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
            tile_size = self.size[0] // 16
            for row in range(13):
                for col in range(16):
                    val = self.screen[row, col]
                    x_start = col * tile_size
                    y_start = row * tile_size

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
        self.channel_idx = 0

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        painter.setPen(QPen(Qt.black, 1, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
        painter.drawRect(0, 0, self.size[0], self.size[1])

        if self.features is not None:
            feat = self.features[0, self.channel_idx].cpu().detach().numpy()
            feat = (feat - feat.min()) / (feat.max() - feat.min() + 1e-8)

            tile_size = self.size[0] // 13
            for row in range(13):
                for col in range(16):
                    val = int(feat[row, col] * 255)
                    color = QColor(val, val, val)
                    painter.setBrush(QBrush(color, Qt.SolidPattern))
                    x_start = col * tile_size
                    y_start = row * tile_size
                    painter.drawRect(x_start, y_start, tile_size, tile_size)

        painter.end()

    def _update(self, features, channel_idx=0):
        self.features = features
        self.channel_idx = channel_idx
        self.update()


class GameWindow(QtWidgets.QMainWindow):
    def __init__(self, env, q, device):
        super().__init__()
        self.setWindowTitle("Super Mario Bros AI - Conv1 Features")
        self.setGeometry(100, 100, 900, 500)

        self.env = env
        self.q = q
        self.device = device

        self.centralWidget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.centralWidget)

        self.env.reset()

        self.screen_viz = ScreenVisualizer(self.centralWidget, (300, 300))
        self.screen_viz.setGeometry(10, 10, 300, 300)

        self.feature_viz = FeatureVisualizer(self.centralWidget, (300, 300))
        self.feature_viz.setGeometry(320, 10, 300, 300)

        self.channel_slider = QtWidgets.QSlider(Qt.Horizontal)
        self.channel_slider.setMinimum(0)
        self.channel_slider.setMaximum(31)
        self.channel_slider.setGeometry(320, 320, 300, 30)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.screen_viz)
        layout.addWidget(self.feature_viz)
        layout.addWidget(self.channel_slider)

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
        self.screen_viz._update(screen)

        s = arrange_state(screen)
        features = self.q.get_conv1_features(s)
        self.feature_viz._update(features, self.channel_slider.value())

        self.env.unwrapped.render()


def main(
    env,
    q,
    q_target,
    optimizer,
    device,
    qt_app=None,
    game_window=None,
    world_model=None,
    wm_optimizer=None,
):
    global frame_stack

    t = 0
    gamma = 0.99
    batch_size = 256
    wm_batch_size = 16
    wm_train_interval = 30

    N = 20000
    eps = 0.1
    memory = replay_memory(N)
    best_mem = best_memory(top_k=50)
    print_interval = 10
    score_lst = []
    total_score = 0.0
    loss = 0.0
    wm_loss = 0.0
    start_time = time.perf_counter()
    best_score = -float("inf")

    for k in range(1000000):
        frame_stack = FrameStack(4)
        env.reset()
        screen = get_rendered_screen(env)
        s = arrange_state(screen)
        done = False
        episode_score = 0
        episode_transitions = []
        while not done:
            if np.random.rand() < eps:
                a = env.action_space.sample()
            else:
                q_values = q(s).cpu().detach().numpy()[0]
                a = np.argmax(q_values)

            s_prime, r, done, _ = env.step(a)
            screen = get_rendered_screen(env)
            s_prime = arrange_state(screen)
            total_score += r
            episode_score += r

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


                if (
                    world_model is not None
                    and wm_optimizer is not None
                    and t % wm_train_interval == 0
                ):
                    wm_loss = train_world_model(world_model, memory, wm_batch_size, wm_optimizer, device)
                t += 1

            if qt_app is not None and t % 10 == 0:
                qt_app.processEvents()

        if episode_score > 700:
            best_mem.push(episode_score, episode_transitions)

        #print(f"Episode score: {episode_score}, Best mem transitions: {best_mem.num_transitions()}")
        avg_score = total_score / print_interval

        if avg_score > best_score:
            best_score = avg_score
            if best_score > 1000:
                best_score = best_score - 0
            copy_weights(q, q_target)
            torch.save(q.state_dict(), "mario_q.pth")
            torch.save(q_target.state_dict(), "mario_q_target.pth")

            if world_model:
                torch.save(world_model.state_dict(), "mario_world.pth")

        if k % print_interval == 0:

            if best_score - avg_score > 300:
                print("===restore best model===")
                copy_weights(q_target, q)
            time_spent, start_time = (
                time.perf_counter() - start_time,
                time.perf_counter(),
            )

            print(
                "%s |Epoch : %d | score : %f  | best score : %f | loss : %.2f | stage : %d | time spent: %f | WM: %f"
                % (
                    device,
                    k,
                    total_score / print_interval,
                    best_score,
                    loss / print_interval,
                    stage,
                    time_spent,
                    wm_loss,
                )
            )
            total_score = 0
            loss = 0.0

    print("Training complete!")


if __name__ == "__main__":
    n_frame = 4
    env = gym_super_mario_bros.make("SuperMarioBros-v0", target=(1, 2))
    env = JoypadSpace(env, SIMPLE_MOVEMENT)
    env = wrap_mario(env)
    device = "cpu"

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

    world_model = WorldModel(n_frame, env.action_space.n, device).to(device)

    optimizer = optim.Adam(q.parameters(), lr=0.0001)
    wm_optimizer = optim.Adam(world_model.parameters(), lr=0.0001)

    print(f"Device: {device}")
    print(f"Actions: {SIMPLE_MOVEMENT}")

    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = GameWindow(env, q, device)
    window.show()

    main(env, q, q_target, optimizer, device, app, window, world_model, wm_optimizer)

    sys.exit(app.exec_())
