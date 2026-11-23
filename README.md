# WebDL

A Japanese static GitHub Pages form that prepares an authenticated GitHub Actions
run for yt-dlp. Video and audio formats are supported, and playlists are
packaged as `<playlist title>.zip`.

## Set up GitHub Pages

1. Push this repository to GitHub and enable Actions in repository settings.
2. In **Settings → Pages**, choose **Deploy from a branch**, select `main` and
   the `/ (root)` folder, then save.
3. Open the published Pages URL. Enter an HTTP(S) URL and choose a format.
4. Run the generated `gh workflow run` command in a terminal authenticated with
   GitHub CLI, or open the Actions workflow page and enter the same inputs.
5. Download the `webdl-download` artifact from the completed workflow run.

The Pages site is static and cannot run Python or securely dispatch a workflow
on its own. Workflow dispatch requires repository write permission; do not put a
personal access token in the Pages site. The Actions workflow runs
[`scripts/download.py`](scripts/download.py) and uploads its result as an
artifact. For playlists, the artifact contains a ZIP named after the playlist.

Only download media that you own or are authorized to download, and follow the
source site's terms. Artifacts follow the repository's access and retention
settings.

## Run locally

```sh
python -m pip install -r requirements.txt
python scripts/download.py --url 'https://example.com/video' --format mp4
```

MP3 and M4A extraction, and video merging, require FFmpeg.