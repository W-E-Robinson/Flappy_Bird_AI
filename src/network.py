import torch.nn as nn
from constants import (
    INPUT_FEATURES,
    HIDDEN_LAYER_SIZE,
    OUTPUT_SIZE,
)


class Network(nn.Module):
    def __init__(self):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(INPUT_FEATURES, HIDDEN_LAYER_SIZE),
            nn.ReLU(),
            nn.Linear(HIDDEN_LAYER_SIZE, OUTPUT_SIZE),
        )

    def forward(self, x):
        return self.network(x)
