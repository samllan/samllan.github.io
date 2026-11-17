"""Verify and fingerprint the assets included in a research report."""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory


def verify_assets(folder, expected):
    folder = folder.resolve()
    inventory = {}
    missing = []
    for name in expected:
        path = (folder / name).resolve()
        if not path.is_relative_to(folder) or name in inventory or name in missing:
            raise ValueError(f"Use distinct paths inside the report folder: {name}")
        if path.is_file():
            content = path.read_bytes()
            inventory[name] = {"bytes": len(content), "sha256": sha256(content).hexdigest()}
        else:
            missing.append(name)
    return inventory, missing


if __name__ == "__main__":
    with TemporaryDirectory() as location:
        report = Path(location)
        (report / "scores.csv").write_text("model,score\nexample,0.82\n", encoding="utf-8")
        inventory, absent = verify_assets(report, ["scores.csv", "figure.pdf"])
        print("Verified:", inventory)
        print("Missing:", absent)
