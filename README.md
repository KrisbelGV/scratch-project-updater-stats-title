# Scratch Project Stats Title Updater

A Python script that monitors your Scratch project statistics (loves, favorites, views) and updates the project title in real time every 5 seconds. Built with [scratchattach](https://github.com/TimMcCool/scratchattach).

> **Educational project** — Created to explore APIs, environment variables, error handling, and server deployment with Python.

## Features

- Updates your Scratch project title every 5 seconds with live stats
- Handles rate limits and API errors gracefully with exponential backoff
- Auto-stops when your Scratch session expires
- Runs locally or on a server 24/7
- Minimal console output — only errors and startup info

## Requirements

- Python 3.9+
- A Scratch account
- [scratchattach](https://github.com/TimMcCool/scratchattach)
- [python-dotenv](https://pypi.org/project/python-dotenv/)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/KrisbelGV/scratch-stats-title-updater.git
   cd scratch-stats-title-updater
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your real data:
   - `SCRATCH_SESSION_ID` — See [Getting your session ID](https://github.com/TimMcCool/scratchattach/wiki/Getting-your-session-id)
   - `SCRATCH_USERNAME` — Your Scratch username (case sensitive)
   - `SCRATCH_PROJECT_ID` — The project ID to monitor
   - `SESSION_EXPIRY` — The expiration date of your session ID (UTC format, from browser cookies)

4. Run the script:
   ```bash
   python main.py
   ```
## Update interval

The default interval between title updates is **5 seconds**. You can change this by editing the last line of the script:

time.sleep(5)

Replace `5` with any value in seconds. A shorter interval means faster updates but more API requests.

## Rate limits

Scratch allows up to **10 requests per second** to its REST API, as documented in the [Scratch REST API wiki](https://github.com/scratchfoundation/scratch-rest-api/wiki). This script makes at most 2 requests per cycle (one read + one write), so even with a 1-second interval you'll stay well within the limit.

Please keep your usage reasonable and benevolent — don't set the interval lower than needed. A value between 2 and 10 seconds is recommended.

## Hosting 24/7

To keep the script running permanently, see the [Hosting guide](https://github.com/TimMcCool/scratchattach/wiki/Hosting) from scratchattach. **Wispbyte** offers a free tier that works great with this project.

## License

This project is licensed under the **MIT License** — feel free to use, modify, and share it.
See [LICENSE](LICENSE) for details.

> **Note:** `scratchattach` is also MIT licensed. This project is not affiliated with Scratch or the scratchattach team.
