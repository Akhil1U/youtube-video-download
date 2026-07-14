<div align="center">

# YouTube Video Downloader API

[![License](https://img.shields.io/static/v1?logo=license&color=Blue&message=Unlicense&label=License)](LICENSE)
[![Release](https://img.shields.io/github/v/release/Simatwa/youtube-downloader-api?label=Release&logo=github)](https://github.com/Simatwa/youtube-downloader-api/releases)
[![Release date](https://img.shields.io/github/release-date/Simatwa/youtube-downloader-api?label=Release%20date&logo=github)](https://github.com/Simatwa/youtube-downloader-api/releases)
[![Total hits](https://hits.sh/github.com/Simatwa/youtube-downloader-api.svg?label=Total%20hits)](https://github.com/Simatwa/youtube-downloader-api)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
</div>


A REST API that provides endpoints for searching, extracting metadata, and downloading YouTube videos in **mp4**, **webm**, **m4a**, and **mp3** formats across multiple quality levels. It is built on FastAPI and powered by `yt-dlp` under the hood, making it suitable for both local use and production deployment.

## Prerequisites

Before getting started, ensure the following are installed on your system:

- [Python 3.10 or higher](https://python.org) - the runtime environment
- [Git](https://git-scm.com/) - for cloning the repository

## Installation Guide

### Step 1: Clone the Repository

Clone the project and navigate into the project directory:

```sh
git clone https://github.com/Simatwa/youtube-downloader-api.git
cd youtube-downloader-api
```

### Step 2: Set Up a Virtual Environment

Create and activate a virtual environment, then install all dependencies:

```sh
pip install uv
uv venv
source .venv/bin/activate
uv sync
```

> [!TIP]
> It is strongly recommended to keep `yt-dlp` updated regularly to avoid breakage caused by YouTube-side changes:
> ```sh
> uv pip install -U yt-dlp
> ```

### Step 3: Configure Settings (Optional)

By default, the app loads configuration from [`config.yml`](./config.yml). Review and adjust the values to suit your environment before starting the server.

For a quick production-ready setup, a pre-tuned [`production.yml`](./production.yml) is included. Simply rename it to `config.yml` to use it:

```sh
mv production.yml config.yml
```

> [!WARNING]
> Some settings in `config.yml` are critical to the app's operation. Incorrect values can break functionality entirely. Make changes only when you understand their effect.

### Step 4: Start the Server

Launch the development server with:

```sh
uv run python -m app run
```

Alternatively, use FastAPI's CLI for more control:

```sh
fastapi run app
```

For advanced startup options such as changing the **host** or **port**:

```sh
uv run fastapi run --help
```

Once running, the API documentation is available at:

- **Swagger UI:** <http://localhost:8000/api/docs>
- **ReDoc:** <http://localhost:8000/api/redoc>

## Serving Frontend Contents

The API can serve a static frontend alongside the backend. To enable this, set the `frontend_dir` key in your [configuration file](./config.yml) to the path of the directory containing your frontend build.

> [!NOTE]
> The specified frontend directory **must** contain an `index.html` file at its root. Without it, the frontend will not be served correctly. Use `YDA_CONFIG_FILE_PATH` environment variable to declare path to yaml file serving as configuration file.

## Optimizing Server Performance

For production deployments, offloading static file delivery (downloaded audio and video files) to a dedicated static server significantly reduces load on the main API process.

**Setup steps:**

1. Start the included static file server:
```sh
   python servers/static.py
```
2. Set the `static_server_url` key in `config.yml` to point to the static server's URL.

> [!IMPORTANT]
> In production, it is recommended to serve static content using [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) for better concurrency and stability. The included [`uwsgi.sh`](../uwsgi.sh) script provides a ready-to-use uWSGI configuration to get you started quickly.

## Cloud Deployment (Render & Railway)

This project is pre-configured for deployment on [Render](https://render.com) and [Railway](https://railway.app) free tiers via the included `render.yaml`, `railway.json`, and `nixpacks.toml` files.

### Quick Deploy

| Platform | Steps |
|----------|-------|
| **Render** | Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint** → Connect your repo. Render detects `render.yaml` automatically. |
| **Railway** | Go to [railway.app/new](https://railway.app/new) → **Deploy from GitHub repo** → Select your repo. Railway reads `railway.json` / `nixpacks.toml` automatically. |

> [!IMPORTANT]
> If you set **Build Command** / **Start Command** manually in the Render dashboard (instead of deploying via Blueprint), they must match `render.yaml` exactly, including the `deno` install step:
> - **Build Command**: `pip install uv && uv sync --frozen && mkdir -p bin && export DENO_INSTALL="$PWD/.deno" && curl -fsSL https://deno.land/install.sh | sh && cp "$DENO_INSTALL/bin/deno" bin/deno`
> - **Start Command**: `PATH="$PWD/bin:$PATH" bash start.sh`
>
> Deploying via **Blueprint** (the recommended path above) picks these up automatically from `render.yaml` — no manual dashboard entry needed.

### Required Environment Variables

Set these in your platform's dashboard:

| Variable | Required | Description |
|----------|----------|-------------|
| `YDA_COOKIES_CONTENT` | ✅ Recommended | Base64-encoded Netscape `cookies.txt`, exported per [Exporting Cookies Correctly](#exporting-cookies-correctly). Without this, requests are likely to be blocked by YouTube's bot detection. |
| `PORT` | Auto-set | Port for the server. Set automatically by both Render and Railway. |
| `YDA_CONFIG_FILE_PATH` | Optional | Path to a custom config YAML. Defaults to `config.yml`. |
| `YDA_CONFIG_CONTENT` | Optional | Base64-encoded custom `config.yml` — overrides the bundled one if set. |

### Exporting Cookies Correctly

Follow yt-dlp's official procedure exactly — this is the part most guides get wrong, and doing it incorrectly is why cookies get invalidated within hours instead of weeks. See [yt-dlp's cookie export guide](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#exporting-youtube-cookies):

1. Open a **private/incognito browser window** — do not use your regular window.
2. Log into YouTube inside that private window.
3. Still in that same tab, navigate to `https://www.youtube.com/robots.txt`.
4. Export cookies using one of yt-dlp's recommended extensions:
   - Chrome/Edge/Brave: [**Get cookies.txt LOCALLY**](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
   - Firefox: **cookies.txt**
   - ⚠️ Do **not** use the old "Get cookies.txt" extension (without "LOCALLY") — it's been flagged as malware and removed from the Chrome Web Store.
5. **Close the private window immediately** and never reopen that session again.

> [!IMPORTANT]
> Step 5 is the critical one. YouTube rotates account cookies frequently on any browser tab that stays open/active. If you keep browsing YouTube in that same session afterward, the cookies you already exported get silently invalidated — which is exactly the "cookies are no longer valid" error. Treat the exported `cookies.txt` as a one-time snapshot, not a live session.

Then encode the file:

```powershell
# Windows PowerShell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("cookies.txt")) | Set-Clipboard
```

```sh
# Linux / macOS
base64 -w 0 cookies.txt | pbcopy   # macOS
base64 -w 0 cookies.txt            # Linux — copy the output
```

Paste the result as the value of `YDA_COOKIES_CONTENT` in the platform dashboard, then redeploy/restart the service.

### Notes on Free Tiers

> [!NOTE]
> - **Render free tier** spins down after 15 minutes of inactivity. The first request after idle takes ~30s to wake up.
> - **Railway free tier** provides $5/month of compute credit — enough for light usage.
> - The filesystem is ephemeral on both platforms. Downloaded media is cleared on each restart (this is already the default behavior).
> - `ffmpeg` and `deno` are installed automatically via `nixpacks.toml` — `ffmpeg` for audio/video merging, `deno` as the JS runtime `yt-dlp` needs to solve YouTube's player challenges. `start.sh` auto-detects `deno` on `PATH` and wires it into `config.yml` (`js_runtime`) at every startup — no env var needed.

## Troubleshooting

### Authorization Issues

YouTube actively flags and blocks requests that lack proper browser-like authorization context. This is a common cause of download failures, especially on fresh deployments or IPs with no prior request history.

**Recommended workarounds, in order of effort:**

1. **Fresh cookies, exported correctly** (see [Exporting Cookies Correctly](#exporting-cookies-correctly) above) + the `deno` JS runtime (already wired up via `nixpacks.toml`/`render.yaml`). This alone resolves the vast majority of "sign in to confirm you're not a bot" errors.
2. **Cookies + PO Token** — a `po_token` proves the request's origin and is increasingly required by YouTube for some player clients. This project supports it via the `po_token` / `visitorData` fields in `config.yml` (see `app/models.py`'s `ytdlp_params` for the exact combination logic), but **only as a static, manually-pasted value** — there's no automated token-generation plugin wired in. Per yt-dlp's own [PO Token Guide](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#po-token-guide), manually extracted tokens are bound to a single video ID and expire quickly, so this is high-maintenance and not a "set once" fix. Only worth doing if cookies alone aren't enough.
3. **Whitelisted Proxy** — route requests through a proxy server that YouTube has not flagged.

> [!NOTE]
> Using a proxy does not guarantee success, and cloud provider IP ranges (Render, Railway, AWS, etc.) are broadly rate-limited/flagged by YouTube regardless of cookies. Fresh, correctly-exported cookies is still the highest-leverage fix for a free-tier deployment.

### "Sign in to confirm you're not a bot" / "cookies are no longer valid"

This means YouTube rejected the session behind your `cookies.txt` — not a bug in the app. The documented cause (per yt-dlp's wiki) is **cookie rotation**: YouTube periodically rotates account cookies on any browser tab/session that stays active. If you exported cookies and then kept using that same browser session, the exported snapshot is invalidated behind your back.

Fix:
1. Re-export cookies using the exact procedure in [Exporting Cookies Correctly](#exporting-cookies-correctly) — private window → log in → visit `robots.txt` → export → **close the window immediately**.
2. Re-encode and update `YDA_COOKIES_CONTENT` in the platform dashboard.
3. Redeploy/restart the service so `start.sh` picks up the new value.

There is no way to make a cookie export last forever — expect to repeat this periodically (the wiki gives no fixed lifetime, but if you're browsing YouTube normally in other tabs with the same Google account, expect it sooner rather than later).

**"No supported JavaScript runtime could be found"** — fixed by the `deno` install (`nixpacks.toml` for Railway, `render.yaml`'s `buildCommand` for Render) plus the auto-wiring in `start.sh`. If you still see this warning, check your build logs for a `deno` install failure, or confirm the platform actually ran your updated build/start commands (see the Render manual-dashboard note above).

## Utility Servers

Two helper servers are included for extending the API's capabilities in production:

| Server | Description |
|--------|-------------|
| [Static Server](../servers/static.py) | Serves downloaded media files independently from the main API process, reducing load and improving throughput |
| [Proxy Server](../servers/proxy.py) | Forwards requests to a non-HTTPS instance of the YouTube Downloader API hosted on a remote server |

## Web Interfaces

The following projects provide ready-to-use web frontends for interacting with the YouTube Downloader API:

| Index | 🎁 Project | ⭐ Stars |
|-------|-----------|---------|
| 0 | [y2mate-clone](https://github.com/Simatwa/y2mate-clone) | [![Stars](https://img.shields.io/github/stars/Simatwa/y2mate-clone?style=flat-square&labelColor=343b41)](https://github.com/Simatwa/y2mate-clone/stargazers) |

_Built a frontend that works with this API? Feel free to open a PR and add it to this list._

## Additional Resources

- [How to extract PO Token](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#po-token-guide) - Required reading if you encounter YouTube authorization errors
- [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp) - The underlying download engine powering this API
- [uWSGI documentation](https://uwsgi-docs.readthedocs.io/en/latest/) - Recommended for production static file serving
- [render.yaml](./render.yaml) - Render Blueprint for one-click cloud deployment
- [railway.json](./railway.json) - Railway project configuration
- [nixpacks.toml](./nixpacks.toml) - Nixpacks build configuration (ffmpeg, deno, uv, Python 3.14)
- [start.sh](./start.sh) - Cloud startup script (handles cookie/config injection from env vars)

## License

- [x] [The Unlicense](LICENSE)