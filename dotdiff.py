"""Compare Windows and NixOS package lists."""
import argparse
import json
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


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


def latest_release(repo):
    if not re.fullmatch(r"[A-Za-z0-9-]+/[A-Za-z0-9_.-]+", repo) or repo.split("/")[1] in {".", ".."}:
        raise ValueError("Expected a GitHub repository in owner/repo format")

    request = Request(
        f"https://api.github.com/repos/{repo}/releases/latest",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "dotdiff"},
    )
    try:
        with urlopen(request, timeout=10) as response:
            release = json.load(response)
    except HTTPError as error:
        if error.code == 404:
            raise ValueError(f"No public latest release found for {repo}") from error
        raise ValueError(f"GitHub API returned HTTP {error.code} for {repo}") from error
    except (URLError, TimeoutError) as error:
        raise ValueError(f"Could not reach the GitHub API: {error}") from error

    return release["tag_name"], release["html_url"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("windows", type=Path, nargs="?", help="Windows package list")
    parser.add_argument("nixos", type=Path, nargs="?", help="NixOS package list")
    parser.add_argument("--aliases", type=Path, help="JSON mapping Windows names to NixOS names")
    parser.add_argument("--github", metavar="OWNER/REPO", help="show the latest public GitHub release")
    args = parser.parse_args()

    if args.github is not None:
        if args.windows is not None or args.nixos is not None or args.aliases is not None:
            parser.error("--github cannot be combined with package lists or --aliases")
        try:
            tag, url = latest_release(args.github)
        except ValueError as error:
            parser.error(str(error))
        print(f"{args.github}: {tag}\n{url}")
        return

    if args.windows is None or args.nixos is None:
        parser.error("provide both package lists or use --github OWNER/REPO")

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
