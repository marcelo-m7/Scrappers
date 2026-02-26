# Instaloader - Instagram Profile Downloader

This repository contains a Python script for downloading all images from a specified Instagram profile. It is built to be robust, featuring built-in tolerance for API rate-limiting and supporting various authentication methods to access public or permitted profiles.

## Features

-   **Image-Focused Downloading**: Downloads only images in their best available resolution, skipping videos.
-   **Resilient to Rate-Limiting**: Implements a progressive backoff strategy (waiting 60s, 120s, 300s, etc.) when a rate-limit is detected, allowing it to resume and complete long download sessions.
-   **Multiple Authentication Methods**:
    -   Interactive login with password and Two-Factor Authentication (2FA) support.
    -   Session reuse via a saved JSON credential file.
    -   Direct use of a `sessionid` cookie for password-less authentication.
-   **Efficient Updates**: A `--fast-update` mode to download only new posts, significantly reducing API calls on subsequent runs for the same profile.
-   **Metadata**: Saves post metadata in a JSON file alongside the downloaded images.

## Prerequisites

-   Python 3
-   The `instaloader` library

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/marcelo-m7/Instaloader.git
    cd Instaloader
    ```

2.  Install the required dependency:
    ```bash
    pip install instaloader
    ```

## Usage

The script is run from the command line, with the target Instagram username as the primary argument.

### Basic Download (Public Profile)

To download all images from a public profile, simply provide the username.

```bash
python main.py <target_username>
```

Files will be saved in a new directory named `./<target_username>/`.

### Authentication

For private profiles or to reduce the chance of hitting rate limits, authenticating with an Instagram account is recommended.

#### 1. Interactive Login (Recommended for First Use)

This method will prompt for your password (and 2FA code if enabled). Upon successful login, it saves your session to a `.session-<your_username>.json` file for easy reuse.

```bash
python main.py <target_username> --login <your_instagram_username>
```

#### 2. Using a Saved Session File

After logging in once, you can use the generated session file for subsequent runs to avoid re-entering your credentials.

```bash
python main.py <target_username> --session-file .session-<your_instagram_username>.json
```

#### 3. Using a `sessionid` Cookie

As an alternative to password-based login, you can provide your account's `sessionid` cookie value directly.

```bash
python main.py <target_username> --sessionid "your_sessionid_cookie_value"
```

### Advanced Options

#### Fast Update (Incremental Downloads)

Use `--fast-update` to instruct the script to stop once it encounters the first already-downloaded picture. This is ideal for periodically syncing a profile to fetch only new content.

```bash
python main.py <target_username> --fast-update --login <your_instagram_username>
```

#### Specify a Custom Destination Directory

By default, files are saved to a folder named after the target user. You can specify a different location with the `--dest` flag.

```bash
python main.py <target_username> --dest /path/to/custom/directory
```

## How It Works

This script leverages the powerful `instaloader` library to interact with the Instagram API. Its key enhancement is a polite but persistent error-handling loop. When it detects an exception related to connection issues or rate-limiting (e.g., HTTP 429), it enters a backoff period. The script will pause for progressively longer intervals (1 minute, 2 minutes, 5 minutes, etc.) before retrying, making it resilient enough to download very large profiles over an extended period without being permanently blocked.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
