# dotdiff

Compare Windows and NixOS package lists with Python 3. No third-party dependencies.

Create two UTF-8 text files with one package name per line. Blank lines and lines starting with `#` are ignored.

`windows.txt`

```text
Git.Git
7zip.7zip
```

`nixos.txt`

```text
git
ripgrep
```

To match Windows package IDs to NixOS names, create an optional `aliases.json`:

```json
{"Git.Git": "git"}
```

```sh
python dotdiff.py windows.txt nixos.txt --aliases aliases.json
```

```text
Only on Windows (1)
  7zip.7zip
Only on NixOS (1)
  ripgrep
On both (1)
  git
```

Omit `--aliases` to compare names exactly. Use `python3` or `py` if that is how you launch Python.

## Look up a GitHub release

Fetch the latest release of a public repository using the GitHub REST API. The command prints the release tag and its URL. It requires internet access and uses the API without a token.

```sh
python dotdiff.py --github BurntSushi/ripgrep
```
