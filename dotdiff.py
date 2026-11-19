"""Compare Windows and NixOS package lists."""
import argparse
from pathlib import Path


def read_packages(path):
    packages = set()
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        name = line.strip()
        if name and not name.startswith("#"):
            packages.add(name)
    return packages


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("windows", type=Path, help="Windows package list")
    parser.add_argument("nixos", type=Path, help="NixOS package list")
    args = parser.parse_args()

    try:
        windows = read_packages(args.windows)
        nixos = read_packages(args.nixos)
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
