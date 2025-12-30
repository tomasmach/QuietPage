"""
Vite manifest loader for Django + Vite integration.

This module provides utilities to read the Vite manifest.json file
and extract asset paths for production builds.
"""

import json
from pathlib import Path
from typing import TypedDict

from django.conf import settings


class ViteAssets(TypedDict):
    """Type definition for Vite assets."""
    js: list[str]
    css: list[str]


# Cache for manifest data to avoid repeated file reads
_manifest_cache: dict | None = None


def _get_manifest_path() -> Path:
    """Get the path to the Vite manifest file."""
    return settings.BASE_DIR / 'frontend' / 'dist' / '.vite' / 'manifest.json'


def _load_manifest() -> dict:
    """
    Load and cache the Vite manifest.

    Returns:
        The parsed manifest.json as a dictionary.
        Empty dict if manifest doesn't exist.
    """
    global _manifest_cache

    # Return cached manifest if available (only in production)
    if _manifest_cache is not None and not settings.DEBUG:
        return _manifest_cache

    manifest_path = _get_manifest_path()

    if not manifest_path.exists():
        return {}

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            _manifest_cache = json.load(f)
            return _manifest_cache
    except (json.JSONDecodeError, IOError):
        return {}


def get_vite_assets() -> ViteAssets:
    """
    Get Vite asset paths for templates.

    In development mode (DEBUG=True), returns empty lists since
    Vite dev server handles assets directly.

    In production mode (DEBUG=False), parses the manifest.json
    and returns paths to JS and CSS files.

    Returns:
        ViteAssets dict with 'js' and 'css' lists containing
        static file paths prefixed with STATIC_URL.
    """
    # In development, Vite dev server serves assets
    if settings.DEBUG:
        return {'js': [], 'css': []}

    manifest = _load_manifest()

    if not manifest:
        return {'js': [], 'css': []}

    js_files: list[str] = []
    css_files: list[str] = []

    # Find the main entry point (index.html)
    entry_key = 'index.html'
    if entry_key not in manifest:
        return {'js': [], 'css': []}

    entry = manifest[entry_key]
    static_url = settings.STATIC_URL.rstrip('/')

    # Get the main JS file
    if 'file' in entry:
        js_files.append(f"{static_url}/{entry['file']}")

    # Get CSS files
    if 'css' in entry:
        for css_file in entry['css']:
            css_files.append(f"{static_url}/{css_file}")

    return {'js': js_files, 'css': css_files}
