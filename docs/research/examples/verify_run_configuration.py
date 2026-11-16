"""Check the settings the model actually received against the run plan."""


def differences(expected, effective):
    return {
        name: {"planned": expected[name], "effective": effective.get(name), "recorded": name in effective}
        for name in sorted(expected)
        if name not in effective or expected[name] != effective[name]
    }


if __name__ == "__main__":
    planned = {"depth": 2, "position_encoding": True, "seed": 7}
    effective = {"depth": 1, "seed": 7}
    for setting, values in differences(planned, effective).items():
        print(setting, values)
