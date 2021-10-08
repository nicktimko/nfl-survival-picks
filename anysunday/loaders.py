import collections

import requests
import pandas as pd
import parsel

from . import types


NUM_TEAMS = 32
# NUM_WEEKS = 17

URL_ESPN_FPI_PAGE = "https://www.espn.com/nfl/fpi"
URL_538_ELOS = "https://projects.fivethirtyeight.com/nfl-api/nfl_elo_latest.csv"


def espn_schedule(filename):
    # copy paste the grid into a file...
    # http://www.espn.com/nfl/schedulegrid

    with open(filename, mode="r") as f:
        raw_schedule = f.read()

    lines = raw_schedule.strip().splitlines()
    team_lines = lines[2:]
    schedule = {}
    games_per_team = collections.Counter()
    weeks = None
    for tl in team_lines:
        cols = tl.split("\t")
        line_weeks = len(cols) - 1
        if weeks:
            if line_weeks != weeks:
                raise Exception(f"non-uniform weeks on team line {cols[0]}")
        else:
            weeks = line_weeks

        team = cols[0]
        for n_wk, match in enumerate(cols[1:], start=1):
            if match == "BYE":
                continue
            schedule.setdefault(n_wk, [])
            games_per_team[match.strip("@")] += 1
            if match.startswith("@"):
                continue  # skip to avoid double counts
            schedule[n_wk].append(types.Match(team, match))

    assert all(n == (weeks - 1) for n in games_per_team.values())

    return schedule


def espn_powers():
    """
    Loads ESPN power ranks and returns them as a TEAM: POWER mapping
    """
    data = requests.get(URL_ESPN_FPI_PAGE)
    selector = parsel.Selector(data.text)
    data_table = selector.xpath("//div[@class='Table__Scroller']/table")

    tables = selector.xpath("//div[contains(concat(' ', @class, ' '), ' league-nfl ')]//table")
    assert len(tables) == 2
    name_table, data_table = tables

    club_table = {}
    for club in name_table.xpath("descendant::*[@data-idx]"):
        club_idx = club.xpath("@data-idx").extract_first()
        club_url = club.xpath("descendant::*[@data-clubhouse-uid]/@href")
        url = club_url.extract_first()
        parts = url.split("/")
        assert parts[4] == "name"
        club_table[parts[5].strip().upper()] = int(club_idx)

    assert len(club_table) == NUM_TEAMS

    powers = {}
    for club, idx in club_table.items():
        xq = f"tbody/*[@data-idx='{idx}']"
        r = data_table.xpath(xq)
        cols = r.xpath("td/div/text()")
        pwr = float(cols[1].extract())
        powers[club] = pwr

    assert set(powers) == set(club_table)

    return powers


def five38_elos():
    return pd.read_csv(URL_538_ELOS)
