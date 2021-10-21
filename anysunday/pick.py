import bisect
import enum
import statistics
import random

from . import powercalcs


HOME_POWER_BUMP = 3


class Modes(enum.Enum):
    BEST = "best"
    RANDOM = "random"
    RANDOM_BIASED = "random_biased"


class Permuter:
    def __init__(self, powers, schedule, home_bump=HOME_POWER_BUMP, past_picks=None):
        self.powers = powers

        self.schedule = schedule
        self.n_weeks = len(schedule)
        self.home_bump = home_bump

        self.update_pick_grid()

        if past_picks is None:
            self.past_picks = []
        else:
            self.past_picks = list(past_picks)

        self.pick = self.greedy()

    def update_pick_grid(self):
        self.grid_index, self.grid = powercalcs.pick_grid(self.powers, self.schedule, self.home_bump)

    def __repr__(self):
        score = self.pick_score
#         return "<{}\n {}\n {}\n min={}, avg={}, max={}>".format(
        return "<{}\n {}\n min={}, avg={}, max={}>".format(
            self.__class__.__name__,
            ", ".join(f"{p:>2s}" for p in self.pick),
#             ", ".join(f"{p:>5s}" for p in self.pick),
#             ", ".join(f"{s:>+4.1f}" for s in score),
            min(self.pick_score),
            statistics.mean(self.pick_score),
            max(self.pick_score),
        )

    def _make_pick(self, week, exclusions=None, mode=Modes.BEST):
        if exclusions is None:
            exclusions = set()

        if mode is Modes.BEST:
            picks = sorted(list(zip(week, self.grid_index)), reverse=True)
        elif mode is Modes.RANDOM:
            picks = list(zip(week, self.grid_index))
            random.shuffle(picks)
        elif mode is Modes.RANDOM_BIASED:
            picks = list(zip(week, self.grid_index))
            random.shuffle(picks)
        else:
            raise ValueError("unknown pick mode")
        for _score, pick in picks:
            if pick in exclusions:
                continue
            return pick
        raise RuntimeError("no valid pick")

    def random(self):
        picks = self.past_picks[:] + [None] * (self.n_weeks - len(self.past_picks))
        weeks_to_pick = list(range(len(self.past_picks), self.n_weeks))
        random.shuffle(weeks_to_pick)
        for ixw in weeks_to_pick:
            week = self.grid[ixw]
            pick = self._make_pick(week, exclusions=picks, mode=Modes.RANDOM)
            picks[ixw] = pick
        return picks

    def greedy(self):
        picks = self.past_picks[:]
        for week in self.grid[len(picks):]:
            pick = self._make_pick(week, exclusions=picks)
            picks.append(pick)
        assert len(picks) == len(self.grid) == self.n_weeks
        return picks

    def reverse_greedy(self):
        picks = []
        for week in reversed(self.grid[len(self.past_picks):]):
            pick = self._make_pick(week, exclusions=picks + self.past_picks)
            picks.append(pick)
        picks = self.past_picks + picks[::-1]
        assert len(picks) == len(self.grid) == self.n_weeks
        return picks

    def random_greedy(self):
        picks = self.past_picks[:] + [None] * (self.n_weeks - len(self.past_picks))
        weeks_to_pick = list(range(len(self.past_picks), self.n_weeks))
        random.shuffle(weeks_to_pick)
        for ixw in weeks_to_pick:
            week = self.grid[ixw]
            pick = self._make_pick(week, exclusions=picks)
            picks[ixw] = pick
        return picks

    def limited_greedy(self, limit=10):
        picks = self.past_picks[:]
        for week in self.grid[len(picks):]:
            worst_picks = sorted(list(zip(week, self.grid_index)))
            pivot_index = bisect.bisect_left(worst_picks, (limit, "X"))
            order = (worst_picks[pivot_index:] + list(reversed(worst_picks[:pivot_index])))
            for _score, pick in order:
                if pick not in picks:
                    picks.append(pick)
                    break
            else:
                raise RuntimeError()
        assert len(picks) == len(self.grid) == self.n_weeks
        return picks

#     def greedy_anneal(self):
#         picks = self.greedy()

    @property
    def pick_score(self):
        return powercalcs.pick_power_calculator(self.powers, self.schedule, self.pick, home_power=self.home_bump)

    def describe_pick(self):
        powercalcs.pick_power_calculator(
            self.powers, self.schedule, self.pick,
            home_power=self.home_bump,
            verbose=True,
            ignore_weeks=len(self.past_picks),
        )

    @property
    def fitness(self):
#         return sum(score * k for score, k in zip(heapq.nsmallest(3, self.pick_score), [10, 3, 1]))
        return sum(score * 2**n for n, score in enumerate(sorted(self.pick_score, reverse=True)))
