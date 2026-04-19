import sys
import time

import gym_super_mario_bros
import torch
import torch.nn as nn
from gym_super_mario_bros.actions import COMPLEX_MOVEMENT
from nes_py.wrappers import JoypadSpace

from wrappers import *

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

class model(nn.Module):
    def __init__(self, n_frame, n_action, device):
        super(model, self).__init__()
        self.n_frame = n_frame
        input_size = n_frame * 16 * 13

        self.fc1 = nn.Linear(input_size, 5120)
        self.fc2 = nn.Linear(5120, 256)
        self.q = nn.Linear(256, n_action)
        self.v = nn.Linear(256, 1)

        self.device = device

        self.fc1.apply(init_weights)
        self.fc2.apply(init_weights)
        self.q.apply(init_weights)
        self.v.apply(init_weights)

    def forward(self, x):
        if type(x) != torch.Tensor:
            x = torch.FloatTensor(x).to(self.device)
        x = x.view(-1, self.n_frame * 16 * 13)
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        adv = self.q(x)
        v = self.v(x)
        q = v + (adv - 1 / adv.shape[-1] * adv.sum(-1, keepdim=True))

        return q

def init_weights(m):
    if type(m) == nn.Conv2d:
        torch.nn.init.xavier_uniform_(m.weight)
        m.bias.data.fill_(0.01)


def arange(s):
    if not type(s) == "numpy.ndarray":
        s = np.array(s)
    assert len(s.shape) == 3
    ret = np.transpose(s, (2, 0, 1))
    return np.expand_dims(ret, 0)


if __name__ == "__main__":
    ckpt_path = sys.argv[1] if len(sys.argv) > 1 else "mario_q_target.pth"
    print(f"Load ckpt from {ckpt_path}")
    n_frame = 4
    env = gym_super_mario_bros.make("SuperMarioBros-v0")
    env = JoypadSpace(env, COMPLEX_MOVEMENT)
    env = wrap_mario(env)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    q = model(n_frame, env.action_space.n, device).to(device)

    q.load_state_dict(torch.load(ckpt_path, map_location=torch.device(device)))
    total_score = 0.0
    done = False
    frame_stack = FrameStack(4)
    env.reset()
    screen = get_rendered_screen(env)
    s = arrange_state(screen)
    #s = arange(env.reset())
    i = 0
    while not done:
        env.render()
        if device == "cpu":
            a = np.argmax(q(s).detach().numpy())
        else:
            a = np.argmax(q(s).cpu().detach().numpy())
        s_prime, r, done, _ = env.step(a)

        screen = get_rendered_screen(env)
        s_prime = arrange_state(screen)

        total_score += r
        s = s_prime
        time.sleep(0.001)

    stage = env.unwrapped._stage
    print("Total score : %f | stage : %d" % (total_score, stage))
