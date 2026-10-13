import torch.nn as nn
from constants import (
    INPUT_FEATURES,
    HIDDEN_LAYER_SIZE,
    OUTPUT_SIZE,
)


class Network(nn.Module):
    def __init__(self):
        super().__init__()

        # Upping to 2 hidden layers rather than one: judging whether the bird
        # clears the gap means composing position, velocity and ticks remaining
        # into a trajectory, which needs products of inputs.
        self.network = nn.Sequential(
            nn.Linear(INPUT_FEATURES, HIDDEN_LAYER_SIZE),
            nn.ReLU(),
            nn.Linear(HIDDEN_LAYER_SIZE, HIDDEN_LAYER_SIZE),
            nn.ReLU(),
            nn.Linear(HIDDEN_LAYER_SIZE, OUTPUT_SIZE),
        )

    def forward(self, x):
        return self.network(x)
