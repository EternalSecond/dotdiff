"""Compare Windows and NixOS package lists."""
import argparse
import json
from pathlib import Path


def read_packages(path):
    packages = set()
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        name = line.strip()
        if name and not name.startswith("#"):
            packages.add(name)
    return packages


def read_aliases(path):
    aliases = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(aliases, dict) or any(
        not name.strip() or not isinstance(target, str) or not target.strip()
        for name, target in aliases.items()
    ):
        raise ValueError("Aliases must be a JSON object mapping package names to nonempty strings")
    return {name.strip(): target.strip() for name, target in aliases.items()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("windows", type=Path, help="Windows package list")
    parser.add_argument("nixos", type=Path, help="NixOS package list")
    parser.add_argument("--aliases", type=Path, help="JSON mapping Windows names to NixOS names")
    args = parser.parse_args()

    try:
        windows = read_packages(args.windows)
        nixos = read_packages(args.nixos)
        if args.aliases:
            aliases = read_aliases(args.aliases)
            windows = {aliases.get(name, name) for name in windows}
    except (OSError, ValueError) as error:
        parser.error(str(error))

    for label, packages in (
        ("Only on Windows", windows - nixos),
        ("Only on NixOS", nixos - windows),
        ("On both", windows & nixos),
    ):
        print(f"{label} ({len(packages)})")
        for package in sorted(packages):
            print(f"  {package}")


if __name__ == "__main__":
    main()
