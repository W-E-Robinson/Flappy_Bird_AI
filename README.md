## Flappy Bird AI

Teaching a reinforcement learning agent to play Flappy Bird like CLI game, then it competing
against myself. The game, the terminal renderer, and the training loop are all
built from scratch on top of [Gymnasium](https://gymnasium.farama.org/) and [PyTorch](https://pytorch.org/).

**Aim: an agent that beats my own best score on the same test course.**

**Stretch Aim: an agent that maxes out the game at 9,999 score on a range of test courses.**

### Contents
- [Intro](#intro)
- [How it works](#how-it-works)
- [Layout](#layout)
- [Getting started](#getting-started)
- [Project Journal](#project-journal)

### Intro
Flappy Bird is a single button game: there are only two actions on any given tick
(flap or do nothing), so the agent gets one decision per
game tick, exactly like a human mashing the spacebar.

The game runs in the terminal. The screen is a 40x40 grid of coloured blocks
drawn with ANSI escape codes, the bird is a 3x3 square pinned to a fixed
column, and the obstacles scroll right to left. Gravity is
[motion with constant acceleration](https://openstax.org/books/university-physics-volume-1/pages/3-4-motion-with-constant-acceleration)
applied per tick, with a flap setting a fixed upward velocity and falling
clamped so the bird doesn't accelerate forever.

The rules the agent and I both play by:
- A flap moves the bird up 2 rows, gravity pulls it back down at 1.2 rows per
  tick squared, capped at 4 rows per tick.
- Obstacles appear every 20 ticks with a gap of 15 rows, shrinking by 2 rows
  every 10 points down to a floor of 5 rows. So the game gets harder the better
  you do.
- Touching the ceiling or the floor ends the run, as does overlapping an obstacle.
- The score caps out at 9,999.
- Game tick is every 100ms (this only applies to me as agent triggers the game tick itself)

<div align="center">
  <video src="https://github.com/user-attachments/assets/8aaeaeae-c7f2-4641-9ed3-8a3d90dfc723" controls width="300" muted alt="Backup: assets/example_gameplay.mp4"></video>
</div>

Because a fair race needs a fair course, `RUN_MODE` switches obstacle
generation between `RANDOM` (fresh randomness, used for training) and `TEST` (a
fixed seeded sequence of obstacle positions). Human runs and bot runs recorded
in `TEST` mode face the identical course, which is what makes the side by side
replay meaningful.

In the video replays of me against the trained mode, I am red, the bot blue, and any
overlap is magenta.

### How it works
- **Game** (`game.py`) - the bird, gravity, obstacles, collision detection,
  scoring, the terminal renderer, and the human input loop.
- **Environment** (`env.py`) - a Gymnasium `Env` wrapping the game. It defines
  what the agent observes, the two actions it can take, and the reward it gets.
- **Agent** (`agent.py`) - picks an action from a given state (ε-greedy over the
  Q-network) and learns from the reward, with a target network to stabilise the
  updates.
- **Network** (`network.py`) - the model the agent uses to guide its decisions.
- **Training** (`train.py`) - runs episodes, updates the model, and saves a
  timestamped checkpoint of the training session to `src/__models__/`.
- **Testing** (`test.py`) - loads the latest model, evaluates it over many
  attempts on the seeded course, and records the best run's moves to
  `src/latest_best_run.txt`.
- **Playing** (`play.py`) - play it yourself with the spacebar. A personal best
  in `TEST` mode is recorded to `src/best_human_run.txt`.
- **Replaying** (`replay.py`) - replays recorded runs tick for tick: the bot,
  me, or both racing on the same screen.

### Layout
```
src/
  game.py              # Game state, physics, rendering, human input loop
  constants.py         # Shared constants and configuration
  env.py               # Gymnasium environment
  agent.py             # The learning agent
  network.py           # The model
  train.py             # Training entrypoint
  test.py              # Evaluation entrypoint
  play.py              # Human play entrypoint
  replay.py            # Replay / race entrypoint
  best_human_run.txt   # Best human run (score + move per tick)
  latest_best_run.txt  # Best bot run (score + move per tick)
  __models__/          # Saved model checkpoints (.pt)
```

### Getting started
**POSIX only.** The renderer clears the terminal with `clear` and
the human input loop reads raw keypresses through `termios`/`tty`/`select`, so
Windows isn't supported.

```bash
# Prepare needed packages
make requirements

# Play it yourself (random obstacles)
make play

# Play the seeded course the bot is scored on, recording a personal best
make play-test

# Train a model (saves to src/__models__/<timestamp>-<episodes>.pt)
make train-model

# Evaluate the latest saved model, recording its best run
make test-model

# Watch a recorded run back: the bot, me, or both racing
make replay-model
make replay-human
make replay-both
```

### Project Journal
A running log of what I tried, what broke, mistakes made, and what I learned.

#### 1st Entry - First Trained Agent (score of 17)
**Goal:** Get an agent that actually clears obstacles rather than flapping into
the ceiling, and get it onto the same seeded course I play so the two are
directly comparable.

What the agent observes, once per game tick:
1) The row of the top of the bird
2) The top row of the upcoming gap
3) The bottom row of the upcoming gap
4) The column distance from the bird to the upcoming obstacle

**The reward:** Deliberately simple. Every tick costs a little, staying on the
central row pays a bit, surviving to clear a gap pays well,
and dying is heavily punished.

```python
reward = -1
if state[0] == 20:
    reward += 5   # Weakly encourage staying centre
if state[3] == 19:
    reward += 25  # Strongly encourage going through the gap
if died:
    reward -= 100
```

- Q-network is tiny: 4 inputs → 32 hidden (ReLU) → 2 outputs.
- ε-greedy exploration decaying from `1.0` → `0.1` across 10k episodes, so lots
  of flailing early and mostly exploiting what it knows by the end.
- Target network resynced every 1000 steps, so the step that pulls the estimate
  toward the goalpost isn't also moving the goalpost.

**Results:** Best of 1000 test episodes scored **17**. My own best on the same
seeded course is **50**, so it is playing the game but it is not beating me yet.
Below is a recording of the bot (blue) playing alongside me (red). Any overlap
shows magenta and the recording runs at 5x playing speed.

<div align="center">
  <video src="https://github.com/user-attachments/assets/befb8624-3d53-4007-9501-7c32173ef697" controls width="300" muted alt="Backup: assets/training_iteration_1.mp4"></video>
</div>

**Next Goal:** Get past my score of 50, which means surviving into the shrinking
gap sizes rather than just cruising through the generous early ones.

Issues with the current approach I can see + things to consider going forward:
- There is no replay buffer, so every transition is learned from exactly once
  and immediately thrown away. Introducing one should improve stability,
  efficiency and performance.
- The reward for sitting on row 20 is a crutch. Centre is only the right place
  to be if the next gap happens to be central, and it will fight the agent as
  gaps shrink and move around. This is shown during the video for the bot's death in
  this training round. As can be seen in the video below, shown at 1/3rd speed, the bot
  goes to clear the gap too low trying to stay more centre and gravity pulls it down to clip the top of the pillar
  with the top of the bird, whereas I keep enough height to make sure the gap is cleared.
  
  <div align="center">
    <video src="https://github.com/user-attachments/assets/f53a3b7a-5340-4dd9-80fd-eb9d79f058af" controls width="300" muted alt="Backup: assets/1st_bot_death.mp4"></video>
  </div>

- The agent only sees one obstacle ahead. At the point a gap is cleared the next
  one is already on screen, and a flap decision made 20 ticks out is what
  decides whether that next gap is reachable. Worth plotting whether feeding it
  the following obstacle too makes a difference. I suspect given the current game mechanics
  it won't make a difference as the distance between the obstacles is enough that the bird
  has more than enough time to make it down/up to the next obstacle regardless of how it passed
  through the previous. If I bring the obstacles closer together in the future this consideration
  may come into play.
- Training and testing built the environment by hand, so none of Gymnasium's own
  plumbing is in play. Once registered and built with `gym.make`,
  this applies the episode `TimeLimit` from the registration, enforces `reset` before
  `step`, and runs the env checker over the first `reset` and `step` to confirm the
  observations match the declared space. It passes clean, which is what I expected: the
  bounds below are loose rather than wrong.
- `observation_space` still claims `Box(0, 39)` on all four dimensions when the real
  ranges are much tighter: bird row 0-37, gap top 2-33, gap bottom 6-37, distance 1-30.
  Worth tightening per dimension in v2, because the true bounds are also the divisors
  needed to normalise the inputs, and right now the four features reach the network on
  four different scales.
