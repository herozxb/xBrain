import torch
import torch.nn as nn
import torch.nn.functional as F


class SimpleSelfAttention(nn.Module):
    def __init__(self, in_channels):
        super().__init__()
        self.query = nn.Conv2d(in_channels, in_channels // 8, 1)
        self.key = nn.Conv2d(in_channels, in_channels // 8, 1)
        self.value = nn.Conv2d(in_channels, in_channels, 1)
        self.gamma = nn.Parameter(torch.zeros(1))

    def forward(self, x):
        batch, c, h, w = x.size()
        q = self.query(x).view(batch, -1, h * w).permute(0, 2, 1)
        k = self.key(x).view(batch, -1, h * w)
        v = self.value(x).view(batch, -1, h * w)

        attn = F.softmax(torch.bmm(q, k), dim=-1)

        out = torch.bmm(v, attn.permute(0, 2, 1)).view(batch, c, h, w)
        return self.gamma * out + x


class model(nn.Module):
    def __init__(self, n_frame, n_action, device):
        super(model, self).__init__()
        self.n_frame = n_frame
        self.n_action = n_action
        self.device = device

        self.conv1 = nn.Conv2d(n_frame, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)

        self.attn1 = SimpleSelfAttention(32)
        self.attn2 = SimpleSelfAttention(64)
        self.attn3 = SimpleSelfAttention(128)

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
        x = self.attn1(x)

        x = torch.relu(self.conv2(x))
        x = self.attn2(x)

        x = torch.relu(self.conv3(x))
        x = self.attn3(x)

        x = x.view(x.size(0), -1)

        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))

        v = torch.relu(self.fc_v(x))
        v = self.v(v)

        a = torch.relu(self.fc_a(x))
        a = self.a(a)

        q = v + (a - a.mean(dim=-1, keepdim=True))

        return q
