"""Report incomplete runs against the expected experiment schedule."""


def incomplete_runs(expected, finished_states):
    return [(key, finished_states.get(key, "missing")) for key in expected if finished_states.get(key) != "completed"]


if __name__ == "__main__":
    expected = [("baseline", 0, 7), ("compact", 0, 7), ("compact", 1, 7)]
    statuses = {expected[0]: "completed", expected[1]: "missing metrics"}
    for key, problem in incomplete_runs(expected, statuses):
        print(*key, problem, sep=",")
