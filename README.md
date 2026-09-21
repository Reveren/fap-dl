# fap-dl

A command-line downloader for images and videos from Fapello profiles.

`fap-dl` uses Chromium to discover the contents of a profile, then closes the
browser and downloads the media directly.

## Features

- Downloads images and videos
- Automatically discovers lazy-loaded posts
- Detects video posts
- Streams downloads directly to disk
- Skips media that has already been downloaded
- Uses `.part` files for incomplete downloads
- Separates images and videos by default
- Supports combined output
- Supports image-only and video-only downloads
- Automatically installs the required Playwright Chromium browser when needed

## Requirements

- Python 3.10 or newer
- Internet connection

### Platform support

`fap-dl` is currently developed and tested on macOS.

The underlying Python, Playwright, Chromium, and Requests components are
cross-platform, so the program is expected to work on Linux and Windows as
well. Linux and Windows have not yet been tested with this project.

## Usage

Download a profile:

```bash
fap-dl PROFILE
```

For example:

```bash
fap-dl diamondnips-1
```

You can also provide the full profile URL:

```bash
fap-dl https://fapello.com/diamondnips-1/
```

By default, files are stored in:

```text
~/Downloads/fap-dl/PROFILE/
├── images/
└── videos/
```

### Combined folder

```bash
fap-dl PROFILE --combined
```

### Images only

```bash
fap-dl PROFILE --images-only
```

### Videos only

```bash
fap-dl PROFILE --videos-only
```

### Custom output directory

```bash
fap-dl PROFILE --output ~/Desktop/media
```

This creates:

```text
~/Desktop/media/PROFILE/
```

## Why does Chromium open?

Fapello is protected by Cloudflare and may challenge or block ordinary
automated HTTP requests. During development, headless Chromium was also unable
to access profile content reliably even when using a previously established
browser session.

For that reason, `fap-dl` briefly launches a normal, visible Chromium window.
This allows the profile to load in a regular browser environment and also
allows you to complete a Cloudflare verification challenge if one appears.

Chromium is used only for the discovery stage:

1. Chromium opens the requested profile.
2. `fap-dl` scrolls through the profile to discover all available posts.
3. Images and video posts are identified.
4. Browser session information is transferred to the downloader.
5. Chromium closes.
6. Images and videos are streamed directly to disk without keeping the
   browser open.

Most runs should therefore require no interaction with the Chromium window.
If Fapello presents a verification challenge, complete it in Chromium and
follow the prompt in the terminal.

Browser data is retained in:

```text
~/.fap-dl/browser/
```

This allows browser session information to persist between runs and can reduce
the need for repeated verification.

## Downloads and existing files

Existing non-empty media files are skipped. This makes it possible to run
`fap-dl` against the same profile later and download newly discovered media
without downloading the entire collection again.

Downloads are streamed directly to disk rather than being held entirely in
memory.

While a file is downloading, it uses the `.part` extension:

```text
example.mp4.part
```

After the download completes successfully, it becomes:

```text
example.mp4
```

This prevents an interrupted or incomplete download from being mistaken for a
completed media file.

## Video fallback

Video URLs can normally be determined directly from the profile gallery.

If a predicted video URL fails, `fap-dl` can reopen Chromium and inspect the
individual post to locate its actual MP4 source. Multiple failed videos are
handled in the same fallback browser session rather than opening a separate
browser for each one.

## Disclaimer

This project is not affiliated with or endorsed by Fapello.

Users are responsible for ensuring that their use of this software complies
with applicable laws, copyright restrictions, website terms, and the rights
of content creators.

## License

MIT