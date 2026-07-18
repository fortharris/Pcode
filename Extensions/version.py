"""Single source of truth for the Pcode application version."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

VERSION = "0.2.0"
GITHUB_REPO = "fortharris/Pcode"
GITHUB_URL = f"https://github.com/{GITHUB_REPO}"
RELEASES_URL = f"{GITHUB_URL}/releases"
LATEST_RELEASE_API = (
    f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
)


def parse_version(value: str) -> tuple:
    """Parse a version string like ``v0.2.0`` into a comparable tuple."""
    text = (value or "").strip().lstrip("vV")
    parts = []
    for piece in text.split("."):
        digits = ""
        for ch in piece:
            if ch.isdigit():
                digits += ch
            else:
                break
        parts.append(int(digits) if digits else 0)
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def check_for_updates(timeout: float = 8.0) -> tuple[str, str, str]:
    """Query GitHub for the latest release.

    Returns ``(status, latest_tag, message)`` where status is one of
    ``newer``, ``current``, or ``error``.
    """
    req = urllib.request.Request(
        LATEST_RELEASE_API,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"Pcode/{VERSION}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return (
                "error",
                "",
                "No GitHub releases found yet. Opening the project page.",
            )
        return "error", "", f"Update check failed (HTTP {err.code})."
    except Exception as err:
        return "error", "", f"Update check failed: {err}"

    tag = (payload.get("tag_name") or "").strip()
    if not tag:
        return "error", "", "Update check returned no release tag."

    if parse_version(tag) > parse_version(VERSION):
        return (
            "newer",
            tag,
            f"A newer release is available: {tag} (you have {VERSION}).",
        )
    return (
        "current",
        tag,
        f"You are on the latest release ({VERSION}).",
    )
