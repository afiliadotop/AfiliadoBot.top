import os
import asyncio
import logging
import tempfile
import pathlib
from typing import Optional

logger = logging.getLogger(__name__)

# Supported domains for quick validation
SUPPORTED_DOMAINS = [
    "shopee.com.br",
    "shopee.com",
    "s.shopee.com.br",
    "instagram.com",
    "tiktok.com",
    "youtube.com",
    "youtu.be",
    "twitter.com",
    "x.com",
    "pinterest.com",
    "kwai.com",
]

# Max file size Telegram accepts for bots: 50MB
MAX_FILE_SIZE_MB = 50


def _is_url_supported(url: str) -> bool:
    """Returns True if the URL domain is in the supported list."""
    return any(domain in url for domain in SUPPORTED_DOMAINS)


async def download_video(url: str, output_dir: str) -> Optional[str]:
    """
    Downloads a video from the given URL using yt-dlp.

    Returns the absolute path to the downloaded file, or None on failure.
    Caller is responsible for deleting the file after use.
    """
    try:
        import yt_dlp  # lazy import — only needed when command is used
    except ImportError:
        logger.error("[VideoDownloader] yt-dlp not installed. Run: pip install yt-dlp")
        return None

    output_template = os.path.join(output_dir, "%(title).60s.%(ext)s")

    ydl_opts = {
        # Best single-file format under 50MB: prefer mp4/webm
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": output_template,
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        # Abort if file exceeds Telegram limit (yt-dlp 2023.11+)
        "max_filesize": MAX_FILE_SIZE_MB * 1024 * 1024,
        # Avoid rate-limit blocks
        "sleep_interval": 1,
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        },
    }

    loop = asyncio.get_event_loop()

    def _run_download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Get the actual filename yt-dlp wrote
            return ydl.prepare_filename(info)

    try:
        filepath = await loop.run_in_executor(None, _run_download)

        # yt-dlp may change extension after merge — try .mp4 fallback
        if not os.path.exists(filepath):
            mp4_path = pathlib.Path(filepath).with_suffix(".mp4")
            if mp4_path.exists():
                filepath = str(mp4_path)
            else:
                logger.error(f"[VideoDownloader] File not found after download: {filepath}")
                return None

        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        logger.info(f"[VideoDownloader] Downloaded {file_size_mb:.1f}MB → {filepath}")

        if file_size_mb > MAX_FILE_SIZE_MB:
            logger.warning(f"[VideoDownloader] File too large ({file_size_mb:.1f}MB), removing.")
            os.remove(filepath)
            return None

        return filepath

    except Exception as e:
        logger.error(f"[VideoDownloader] yt-dlp error for {url}: {e}")
        return None


def cleanup(filepath: str) -> None:
    """Safely removes a downloaded file."""
    try:
        if filepath and os.path.exists(filepath):
            os.remove(filepath)
            logger.debug(f"[VideoDownloader] Cleaned up: {filepath}")
    except Exception as e:
        logger.warning(f"[VideoDownloader] Cleanup failed for {filepath}: {e}")
