# fap-dl

A command-line downloader for downloading images and videos from Fapello profiles.

`fap-dl` discovers all available posts on a profile and downloads the media to your computer. It supports separate image and video folders, combined downloads, image-only or video-only modes, and automatically skips files that have already been downloaded.

## Features

- Downloads images and videos from Fapello profiles
- Accepts either a profile name or full Fapello profile URL
- Automatically discovers lazy-loaded posts
- Downloads media directly to disk
- Skips files that have already been downloaded
- Stores images and videos in separate folders by default
- Optional combined image/video folder
- Image-only and video-only modes
- Uses `.part` files for incomplete downloads
- Uses Chromium for profile discovery when necessary
- Automatically installs the required Playwright Chromium browser
- Maintains a persistent browser profile to reduce repeated Cloudflare challenges
- Supports macOS, Windows, and Linux

## Requirements

- Python 3.10 or newer
- An internet connection
- Chromium, which `fap-dl` can install automatically when first needed

## Installation

### Recommended: pipx

The recommended way to install `fap-dl` is with `pipx`:

```bash
pipx install fap-dl
```

Once installed, verify that it is available:

```bash
fap-dl --help
```

If you do not already have `pipx`, see the official pipx installation instructions:

https://pipx.pypa.io/latest/how-to/install-pipx.html

```bash
brew install pipx
```

### Install from GitHub

You can also install the latest version directly from GitHub:

```bash
pipx install git+https://github.com/Reveren/fap-dl.git
```

This may include changes newer than the current PyPI release.

## Usage

The basic command is:

```bash
fap-dl PROFILE
```

`PROFILE` can be either a Fapello profile name or a full profile URL.

For example:

```bash
fap-dl diamondnips-1
```

or:

```bash
fap-dl https://fapello.com/diamondnips-1/
```

By default, files are downloaded to:

```text
~/Downloads/fap-dl/diamondnips-1/
├── images/
└── videos/
```

## Options

```text
usage: fap-dl [-h] [--combined] [--images-only | --videos-only]
			  [--output OUTPUT] profile

Download images and videos from a Fapello profile.

positional arguments:
  profile          Fapello profile name or full profile URL

options:
  -h, --help       show this help message and exit
  --combined       Store images and videos together instead of separate folders.
  --images-only    Download images only.
  --videos-only    Download videos only.
  --output OUTPUT  Download directory. Default: ~/Downloads/fap-dl
```

### Download images and videos

```bash
fap-dl diamondnips-1
```

This is the default behavior.

### Download images only

```bash
fap-dl diamondnips-1 --images-only
```

### Download videos only

```bash
fap-dl diamondnips-1 --videos-only
```

### Store everything in one folder

```bash
fap-dl diamondnips-1 --combined
```

Instead of separate `images` and `videos` directories, all media will be stored together.

### Choose a different download location

```bash
fap-dl diamondnips-1 --output ~/Desktop/Fapello
```

The profile directory will be created inside the specified location.

Options can also be combined:

```bash
fap-dl diamondnips-1 --videos-only --output ~/Desktop/Fapello
```

## Browser and Cloudflare

Fapello may use Cloudflare protection that prevents profile discovery using normal HTTP requests or a headless browser.

For this reason, `fap-dl` uses a visible Chromium browser when discovering profile content.

The browser may briefly appear while the profile is being scanned. Once discovery is complete, normal media downloads are performed directly without keeping the browser open unnecessarily.

On first use, `fap-dl` will attempt to install the Chromium browser required by Playwright if it is not already installed.

Browser data is stored in:

```text
~/.fap-dl/browser/
```

This persistent browser profile allows cookies and other browser state to be reused between runs and may reduce repeated Cloudflare challenges.

If Cloudflare presents a verification screen, complete the verification in the Chromium window and allow `fap-dl` to continue.

## Existing and Incomplete Downloads

`fap-dl` checks for files that have already been downloaded and skips them instead of downloading them again.

Downloads are initially written using a `.part` extension.

For example:

```text
video.mp4.part
```

After the download completes successfully, the file is renamed to its final filename:

```text
video.mp4
```

This helps distinguish completed downloads from files that were interrupted before finishing.

If you run `fap-dl` again, completed files will be skipped and missing media can be downloaded.

## Updating

If you installed `fap-dl` from PyPI using pipx:

```bash
pipx upgrade fap-dl
```

To reinstall the latest version:

```bash
pipx reinstall fap-dl
```

If you installed directly from GitHub and want the newest GitHub version:

```bash
pipx install --force git+https://github.com/Reveren/fap-dl.git
```

## Uninstalling

To remove `fap-dl`:

```bash
pipx uninstall fap-dl
```

The persistent browser data stored in `~/.fap-dl/` is separate from the Python package and may remain after uninstalling.

If you no longer want that data, it can be removed manually.

## Development

Clone the repository:

```bash
git clone https://github.com/Reveren/fap-dl.git
cd fap-dl
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it on macOS or Linux:

```bash
source .venv/bin/activate
```

On Windows:

```powershell
.venv\Scripts\activate
```

Install the project in editable mode:

```bash
python -m pip install -e .
```

You can then run:

```bash
fap-dl --help
```

## Disclaimer

`fap-dl` is an independent open-source project and is not affiliated with, endorsed by, or associated with Fapello.

This software is provided for personal and educational use. Users are responsible for complying with applicable laws, website terms of service, and copyright restrictions.

Only download content that you are legally permitted to access and save.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.