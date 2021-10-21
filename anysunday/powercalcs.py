HOME_POWER_BUMP = 3.0

verb_template = "week {wk:2d}: diff {d:+5.1f} - picking {p:3s} ({ps:+3.1f}%PH%) over {vp:3s} ({vps:+3.1f}%VPH%)"


def pick_power_calculator(
    powers,
    schedule,
    picks,
    home_power=HOME_POWER_BUMP,
    verbose=False,
    ignore_weeks=0,
):
    n_weeks = len(schedule)
    if len(picks) != n_weeks:
        raise ValueError("picks needed for each week")
    if len(set(picks)) != n_weeks:
        raise ValueError("unique picks needed")
    if not all(p in powers for p in picks):
        raise ValueError("unrecognized team initials")

    pick_powers = []
    for n_week, pick in zip(sorted(schedule), picks):
        if n_week <= ignore_weeks:
            continue
        wk_sched = schedule[n_week]
        for match in wk_sched:
            if match.home == pick:
                pick_powers.append(powers[match.home] - powers[match.away] + home_power)
                if verbose:
                    print(verb_template.replace("%PH%", "+H").replace("%VPH%", "  ").format(
                        wk=n_week,
                        d = pick_powers[-1],
                        p=match.home,
                        ps=powers[match.home],
                        vp=match.away,
                        vps=powers[match.away],

                    ))
                break
            if match.away == pick:
                pick_powers.append(powers[match.away] - powers[match.home] - home_power)
                if verbose:
                    print(verb_template.replace("%VPH%", "+H").replace("%PH%", "  ").format(
                        wk=n_week,
                        d = pick_powers[-1],
                        vp=match.home,
                        vps=powers[match.home],
                        p=match.away,
                        ps=powers[match.away],

                    ))
                break
        else:
            raise ValueError(f"team {pick} does not play in week {n_week}")
    return pick_powers

BYE_SCORE = -10

def pick_grid(powers, schedule, home_bump=HOME_POWER_BUMP):
    matrix = []

    index = sorted(powers, key=lambda x: powers[x])

    for n_week, matches in sorted(schedule.items()):
        teams = {}
        for match in matches:
            teams[match.home] = powers[match.home] - powers[match.away] + home_bump
            teams[match.away] = powers[match.away] - powers[match.home] - home_bump
        week_col = [teams.get(t, BYE_SCORE) for t in index]
        matrix.append(week_col)
    return index, matrix
