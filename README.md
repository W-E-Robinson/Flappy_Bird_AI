## Flappy Bird AI

Teaching a reinforcement learning agent to play a Flappy Bird like CLI game, with it competing
against my own best efforts. This is my effort trying reinforcement learning. The game, the terminal renderer, and the training loop are all
built from scratch on top of [Gymnasium](https://gymnasium.farama.org/) and [PyTorch](https://pytorch.org/).

**Aim: a model that beats my own best score on the a set competition course.**

**Stretch Aim: a model that maxes out the game at 999 score on a range of test courses.**

### Contents
- [Intro](#intro)
- [How it works](#how-it-works)
- [Layout](#layout)
- [Getting started](#getting-started)
- [Project Journal](#project-journal)

### Intro
Flappy Bird is a single button game: there are only two actions on any given tick
(flap or do nothing), so the agent gets one decision per
game tick, like a human mashing the spacebar.

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
- The score caps out at 999.
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
  scoring, the terminal renderer, and the human input loop. A course can be
  seeded, so the same seed always generates the same obstacles.
- **Environment** (`env.py`) - a Gymnasium `Env` wrapping the game. It defines
  what the agent observes, the two actions it can take, and the reward it gets.
  A seed passed to `reset` reaches the course as well as Gymnasium's own RNG.
- **Agent** (`agent.py`) - picks an action from a given state (ε-greedy over the
  Q-network) and learns from the reward, with a target network to stabilise the
  updates. Trains on random batches from the replay buffer rather than on the
  tick that just happened.
- **Replay buffer** (`replay_buffer.py`) - a fixed size FIFO of past
  transitions, sampled at random. Decorrelates consecutive ticks and keeps rare
  but informative transitions, deaths especially, available to learn from more
  than once.
- **Network** (`network.py`) - the model the agent uses to guide its decisions.
- **Training** (`train.py`) - runs episodes, updates the model, saves a
  timestamped checkpoint to `src/__models__/` and the per episode scores to
  `src/scores_last_test_session.txt`.
- **Testing** (`test.py`) - loads the latest model and plays it at ε=0 over
  `NUM_TEST_EPISODES` seeded courses, so every model faces the identical set and
  scores are comparable between runs. Reports the distribution rather than just
  the best, writes every score to `src/scores_last_test_run.txt`, and records
  the best run to `src/latest_best_run.txt`, plus `src/best_bot_run.txt` if it
  beats the best ever.
- **Playing** (`play.py`) - play it yourself with the spacebar. A personal best
  in `TEST` mode is recorded to `src/best_human_run.txt`.
- **Replaying** (`replay.py`) - replays recorded runs tick for tick: the bot,
  me, or both racing on the same screen. A run stores the seed it was scored on
  alongside its moves, so the exact course is rebuilt to replay against.
- **Graphing** (`graph.py`) - saves a timestamped PNG to `src/__graphs__/`:
  either score per episode across a training session, or the distribution of
  scores across a test run.

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
  replay_buffer.py     # Experience replay buffer
  graph.py             # Graphs of recorded scores
  best_human_run.txt   # Best human run (score + move per tick)
  best_bot_run.txt     # Best bot run ever (score + seed + move per tick)
  latest_best_run.txt  # Best bot run of the last test (score + seed + moves)
  scores_last_test_session.txt  # Score per episode, last training session
  scores_last_test_run.txt      # Score per course, last test run
  __models__/          # Saved model checkpoints (.pt)
  __graphs__/          # Saved graphs (.png)
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

# Play the fixed course, recording a personal best to best_human_run.txt
make play-test

# Train a model (saves to src/__models__/<timestamp>-<episodes>.pt)
make train-model

# Evaluate the latest model over 1000 seeded courses, reporting the
# distribution and recording its best run with the seed it scored on
make test-model

# Both, back to back
make train-test-model

# Watch a recorded run back: the latest bot run, the best ever, me,
# or the bot and me racing side by side
make replay-latest-model
make replay-best-ever
make replay-human
make replay-both

# Graph the last training session, or the last test run's distribution
make graph-session
make graph-test-run

# Housekeeping
make unit-test     # run the tests
make style         # format with black, then type check with pyright
make clear-models  # delete saved checkpoints
```

Note that `make play-test` puts you on the fixed `RUN_MODE=TEST` course, while
the bot is now scored on seeded courses, so the two are no longer the same
obstacles. `make replay-both` races runs recorded against different courses for
the same reason.

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

**Results:** Best test episode score is **17**. My own best on the same
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

#### 2nd Entry - Beating My Own Score (median of 53, best of 93)
**Goal:** Get past my own best of 50, which means surviving into the narrowest
gaps.

This entry is a lot of small changes and then one big change. Roughly in the
order I did them:

##### 1. The observations were wrong before the agent ever saw them
Two of the four numbers I was feeding in were incorrect. The "middle of
the bird" was off by one row (as it was assuming a bird size of 1, not 3),
and the distance to the upcoming gap was wsay off, measuring from the wrong column entirely.

##### 2. Two more observations changes
Went from 4 inputs to 6, adding:
- Offset from the centre of the upcoming gap (negative above, positive below)
- Bird velocity

Before the agent had to work out whether it was above or below the offset, by comparing three separate row numbers itself,
a lot to ask of one hidden layer. The velocity matters because the bird is
accelerating under gravity, so the same row with a different speed needs a
completely different decision.

##### 3. The rewards were quietly rewarding the wrong thing
This was the real problem, and there were three separate bugs:

- The alignment reward was keyed on `state[0]`, the bird's absolute row,
  not its offset from the gap. So it only paid out at rows 0, 1 and 2, which is
  jammed against the ceiling, and a perfectly centred bird got punished. It was
  training the bird to fly into the roof, **facepalm**.
- The +20 for clearing a gap checked `state[3] == 19`, but the distance resets
  to 17 when the next gap appears (due to bird size of 3). That line had never once executed. The
  single most informative reward in the whole function was dead code.
- Death was reported as `truncated` rather than `terminated`, so the Q update
  bootstrapped through the wall: the target on a death was
  `-100 + 0.95 * max Q(state_after_dying)`, which partly cancelled out the
  punishment with a garbage value for a state that does not exist.

##### 4. Normalising the inputs
Raw observations spanned 0-38 for the row features but only 0-4 for velocity,
so velocity was effectively invisible next to everything else. Everything now
gets scaled to `[-1, 1]`.

I also gave the velocity a sign while I was in there. It was an unsigned
magnitude with the direction tracked separately and never passed on, so rising
at 2 rows/tick and falling at 2 rows/tick looked identical to the network.

##### 5. Rescaling the rewards
Went from `+5 / +20 / -100` to roughly `+0.2 / +1 / -5`.

The thing the network predicts is not a single tick's reward, it is the total
reward it expects from here on. With a discount of 0.95 that works out at
roughly the next 20 ticks added together, so under the old scale it was being
asked to output numbers as big as about 130.

A freshly initialised network outputs numbers around 0.5. So before it can
learn anything useful it has to spend thousands of episodes just inflating its
own output range by a factor of 250, which is pure wasted effort.

Shrinking the rewards keeps the predictions in a range the network can produce
from the start, and nothing about the decision changes.

One trap here I nearly walked into: the rescale has to stay proportional.
My first pass divided the alignment rewards by 20 and the death penalty by 100,
which made dying (-1) cheaper than drifting misaligned for 20 ticks (-2). It
would have learned to crash on purpose as an escape from accrued negative
reward. The death penalty is -5 for exactly this reason.

```python
# Current rewards, per tick
if abs(state[4]) == 0:
    reward += 0.2    # Dead centre of the gap
elif abs(state[4]) == 1:
    reward += 0.15
elif abs(state[4]) == 2:
    reward += 0.05
else:
    reward -= 0.1    # Outside the band
if scored:
    reward += 1      # Cleared a gap
if game_over:
    reward -= 5      # Must outweigh a whole horizon of misalignment
```

##### 6. A replay buffer
The thing I flagged as the top issue last entry. Every transition is now pushed
into a 100k FIFO buffer and training samples a random batch of 64 from it,
instead of learning once from the tick that just happened and throwing it away.

- Consecutive game ticks are nearly identical, so learning from them in order
  badly violates the assumption that samples are independent.
- Deaths are the rarest and most informative transition, and they get rarer the
  better the bird gets. At 300+ ticks an episode a death is well under 1% of the
  data. The buffer keeps a standing reservoir of them to sample from.

##### 7. A bigger network
32 hidden units in a single layer, up to 64 in two layers (290 parameters to
4,738). Judging whether the bird clears a gap means composing position,
velocity and ticks-remaining into a trajectory, which needs products of the
inputs. One ReLU layer approximates those badly.


##### 8. The epsilon schedule (the big one)
The previous changes to so far in this journal pushed the average score by the the last rolling
200 episodes to be 18.20 agasint random training, then came the big noticed change below

The first problem was the floor of 0.1, which sounds harmless and really is not.

Epsilon 0.1 means 10% of ticks take a random action. But there are only two
actions to pick from, so half the time that random pick lands on the one it was
going to choose anyway. The chance of actually being dragged off course* on
any single tick is therefore `0.1 / 2 = 5%`.

A gap takes about 20 ticks to fly through, and clearing it means getting near all 20
of those ticks right. So I need to not be knocked off course 20 times in a row,
which is 95% multiplied by itself 20 times:

```
P(knocked off course at least once) = 1 - 0.95^20 = 0.64
```

So a 64% chance of being thrown off in any given gap.** e agent was never
getting a fair run at a single obstacle. Dropping the floor to 0.01 gives
`1 - 0.995^20 = 0.095`, so about 10% instead.

This is also why my training graphs always looked worse than the model really
was. Those scores are recorded with exploration still switched on, whereas
the test run plays at epsilon 0.

The second problem was that the decay was derived from the episode count, so it
reached the floor at 90% of the run no matter how long the run was. Bumping
training from 10k to 25k episodes did nothing except stretch the exploration
phase proportionally.

The other huge advantage to keep final exploration small at the end is that the model
gets way more time training around the 50+ region. At 50 is when the gap has shrunk to
the minimum (5) and is the most difficult stage. At epsilon ending in 0.1 it would just immediately die
most of the time and not learn how to handle these.

<div align="center">
  <img src="https://github.com/user-attachments/assets/6c9b241f-94e7-4040-8e35-e1bf753de970" width="700" alt="Backup: assets/2nd_entry_training_curve.png">
</div>

##### 9. Testing properly: 1000 seeded courses
The old test loop ran 1000 episodes with `RUN_MODE=TEST`, which uses a fixed
list of obstacle positions. Since the model is deterministic at epsilon 0, that
was 1000 identical replays of the same game, **second facepalm**. It reported exactly the same
score every time and I was reading it as a distribution, not very good.

Courses are now seedable. The test run plays seeds 0-999, so every model faces
the identical set of 1000 different courses and the numbers are comparable
between runs. It reports the median  and means as the most important statistics, as well as single highest score.

The seed also gets stored alongside the moves in the best run files, which
means a recorded run can be rebuilt exactly for replay. Before this, saved
moves only reproduced against whatever course happened to be generated next.

<div align="center">
  <img src="https://github.com/user-attachments/assets/bfd98883-bfd8-451c-abe3-1276218409a1" width="700" alt="Backup: assets/2nd_entry_score_histogram.png">
</div>

Results: Over 1000 seeded courses the model now scores a **median of 53**,
a mean of 54.13, a best of **93** and, notably, **zero failures**, with the
worst course of the thousand still reaching 41. Last entry's best single run
was 17. My own best is 50, so it is now comfortably past me.

| Milestone | Gap size | Courses reaching it |
|---|---|---|
| Score 10 | 13 | 100% |
| Score 20 | 11 | 100% |
| Score 30 | 9 | 100% |
| Score 40 | 7 | 100% |
| Score 50 | 5 | 91.1% |

So everything down to a 7 row gap is now essentially solved, and 91% of runs
make it to the 5 row gaps.

**Next Goal:** Consistently well past 50 and beyond. The best run of 93 is proof the policy can already string
43 of the narrowest gap together back to back, so consistency is the gap rather than
capability.

Issues with the current approach I can see + things to consider going forward:
- Looking at how the bird dies at the narrow gaps, **71% of deaths happen on a tick where the bird is rising**,
  i.e. it killed itself by flapping, and a third of those are from a position
  that was already within 1 row of the centre. A flap moves it 2 rows instantly
  and the survivable window at a 5 row gap is 1 row either side, so flapping on
  final approach is fatal even from a perfect position. The reward pays for
  alignment right now, but what matters is alignment on arrival. Shaping on
  projected arrival position instead is the obvious next experiment.
- A discount of 0.95 is a 20 tick lookahead, incidentally is almost exactly one gap.
  Threading through 5 row gaps is a timing problem that needs planning across the
  gap boundary, so 0.98 (about 50 ticks) is worth trying, at the cost of slower
  and noisier learning.
- Even at 0.01, is better bit epsilon is still pretty fatal at the narrowest gaps, so a chunk of
  late training experience is the agent learning from deaths it is pushed towards. Making even lower on the final stretch may help.
- The agent still only sees one obstacle ahead. I argued last entry that the
  obstacle spacing makes this a non issue, and I still think that is true at
  wide gaps, but at 5 rows the centres can be ~30 units apart and the bird may
  need to commit before clearing the current gap.

#### 3rd Entry - Overcoming the smallest gap (median of 73, mean of 83, best of 328)
**Goal:** Get the model to conquer the hardest gap size and get many scores in the triple figures
against the 1000 seed test courses from 2nd journal entry.

##### 1. Increased discount factor
As discussed in previous journal reflection, a discount of 0.95 is a 20 tick lookahead.
Whereas the new 0.98 has a 50 tick lookahead, which will go well with the next change to be
made below.

##### 2. Added two new observations
- The offset for the gap after the next upcoming one, 0 when not on screen
- A 1 or 0 that indicates if the gap after next is actually on the screen

With the increased discount factor this yieled a new high median up to new max of 55 and new max of 98.
This disproved my theory in the 1st journal entry that observations of the gap after the upcoming would make
little difference in the current game setup.

If I were to change the rules of the game in the future to bring the obstacles closer
together to the point where going through the middle of gaps may becomes sub optimal, these
new observations will increase even more in value.

##### 3. Extended the time in lowest gap further still
The number of episodes is bumped from 10k to 25k and reduced the epsilon bottom
by half to 0.005 and dropped the training to the last full 20% at the lowest epsilon.
To get the agent even more time in the 50+ region, but this did increase training time by 4-5x.

This bumped my median to 63 and my single best to 207. I still believe the real blocker here
is the reward strategy approaching the narrowest gaps. Still, helpful to know that getting as much
time in the final region does produce some meaningful difference.

##### 4. Conquering the 5 gap
When I arbitrarily made the smallest gap possible on the course 5 I unknowingly made it very difficult for a 3x3 bird to get through.

The bird takes 3 ticks between starting the obstacle to clearing it.
Hitting the spacebar rises the bird by 2, making it very easy whilst inside the gap to do this and hit the top of it.
The tick before the obstacle is reached, if the bottom of the bird is 1 to 2 rows below the bottom of the gap and then spacebar is hit,
this will be enough to carry it through the gap with no further input needed. The bird needs some foresight before this so that it can position itself in this correct
spot 1 tick before the obstacle is reached, once it's too late it's too late. The bird takes 5 ticks to return to the same row from which the spacebar is hit with no flaps since. I will tinker with rewarding to encourage the bird to do this.

After experimenting with the reward structure I found the best success concerning approach by doing:
```python
if state[3] == 6:
    if state[0] == state[2] + 1 or state[0] == state[2] + 2:
        reward += 0.2
    else:
        reward -= 0.2
if state[3] == 1:
    if state[0] == state[2] + 1 or state[0] == state[2] + 2:
        reward += 0.2
    else:
        reward -= 0.2
```
Where state[3] if the distance to the next column, this encourages a flap with 6 ticks to go from the obstacle
with the bird either 1 or 2 rows overlapping the bottom of the gap. To then be in the same place 5 ticks later
to then flap again and clear the gap.

These are the fianl histogram results. The mean is well above my best, well into the hardest region, many runs over 100,
with one course in particular producing a huge score of 328.

<div align="center">
  <img src="https://github.com/user-attachments/assets/4966fa8e-dd6e-4fd6-b552-50a252e8b3c8" width="700" alt="Backup: assets/final_test_run_graph.png">
</div>

Below is a video of the 328 score:

<div align="center">
  <video src="https://github.com/user-attachments/assets/cf4704d1-b9e9-4559-b932-e295ea2552bd" controls width="300" muted alt="Backup: assets/best_eve_bot_run_speedup.mp4"></video>
</div>

One thing worh considering is that the bot had the time to decide its tick actoin, whereas with the 100ms tick time as a human my brain/thumb would hinder me in situations where decisions
needed to be made quickly. Having said that, even with a level decision time playing field, I think the models ability to have forsight 6 ticks out from an obstacle would still give it
the ultimate advantage over me.

I'm happy this being the final journal entry on this project, despite not having reached my stretch goal of a 999 max score runs from a model.
I do have some ideas for improvement such as prioritised replay. However, I have learnt more than I thought I would from this first project dabbling 
in reinforcement learning and want to move onto other more interesting projects, may be I will return one day.
