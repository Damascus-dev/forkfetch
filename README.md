# Fetcher

Minimal GitHub repository search CLI.

## Install

### PyPI

After the package is published, users on Windows, macOS, and Linux will be able to install it from any folder with:

```bash
pip install ffetch-cli
```

That installs the `ffetch` command globally for the current Python environment, so it can be run from any drive or working directory.

### Windows

Install from the project folder:

```bat
install_ffetch.cmd
```

That script runs a user install and checks whether the Python Scripts directory is on `PATH`.
After a successful install, `ffetch` can be run from any drive or folder.

If you prefer the manual command:

```bat
py -m pip install --user .
```

If `ffetch` is still not recognized after install, reopen the terminal. If that still fails, add the Python user Scripts directory shown by `install_ffetch.cmd` to your Windows `PATH`.

### macOS / Linux

```bash
python3 -m pip install --user .
```

If `ffetch` is not found afterward, make sure your user script directory is on `PATH`. A common fix is:

```bash
python3 -m site --user-base
```

Then add the corresponding `bin` directory to your shell profile.

## Use

```bash
ffetch
ffetch search "jwt auth node"
ffetch top
ffetch refresh
ffetch clone owner/repo
ffetch config
python -m fetcher --help
```

## Token

Config file:

`~/.fetcher/config.json`

```json
{
  "github_token": "YOUR_TOKEN"
}
```

## Publish

Build distributions locally:

```bash
python3 -m pip install -U build
python3 -m build
```

Upload manually:

```bash
python3 -m pip install -U twine
python3 -m twine upload dist/*
```

GitHub Actions can also publish automatically on tagged releases once PyPI trusted publishing is configured.
