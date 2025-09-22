from typing import Dict
import re


def extract_version_from_download_url(url: str) -> str:
    """
    Extract version number from download URL.
    """
    if not url:
        return None

    # Common version patterns in download URLs
    version_patterns = [
        r'/archive/(?:v)?(\d+\.\d+(?:\.\d+)?(?:[a-zA-Z0-9\-\.]*)?)',  # /archive/3.8.0 or /archive/v1.2.3
        r'[-_](?:v)?(\d+\.\d+(?:\.\d+)?(?:[a-zA-Z0-9\-\.]*)?)\.',  # -3.8.0.tar.gz or _v1.2.3.zip
        r'/(?:v)?(\d+\.\d+(?:\.\d+)?(?:[a-zA-Z0-9\-\.]*)?)/[^/]*$'  # /3.8.0/something
    ]

    for pattern in version_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


def get_latest_release_version(somef_data: Dict) -> str:
    """
    Get the latest release version from releases data.
    """
    if "releases" not in somef_data:
        return None

    releases = somef_data["releases"]
    if not isinstance(releases, list) or not releases:
        return None

    latest_release = releases[0]
    if "result" in latest_release:
        result = latest_release["result"]

        # Try to get version from tag or name
        if "tag" in result and result["tag"]:
            tag = result["tag"]
            # Clean up tag (remove 'v' prefix if present)
            if tag.startswith('v'):
                return tag[1:]
            return tag

        if "name" in result and result["name"]:
            name = result["name"]
            # Extract version from name
            version_match = re.search(r'(?:v)?(\d+\.\d+(?:\.\d+)?(?:[a-zA-Z0-9\-\.]*)?)', name)
            if version_match:
                return version_match.group(1)

    return None


def detect_outdated_download_url_pitfall(somef_data: Dict, file_name: str) -> Dict:
    """
    Detect when codemeta.json downloadURL is outdated compared to latest release.
    """
    result = {
        "has_pitfall": False,
        "file_name": file_name,
        "download_url": None,
        "download_version": None,
        "latest_release_version": None,
        "source": None
    }

    if "download_url" not in somef_data:
        return result

    download_entries = somef_data["download_url"]
    if not isinstance(download_entries, list):
        return result

    codemeta_download_url = None
    codemeta_source = None

    for entry in download_entries:
        source = entry.get("source", "")
        technique = entry.get("technique", "")

        if "codemeta.json" in source or (technique == "code_parser" and "codemeta" in source.lower()):
            if "result" in entry and "value" in entry["result"]:
                codemeta_download_url = entry["result"]["value"]
                codemeta_source = source
                break

    if not codemeta_download_url:
        return result

    download_version = extract_version_from_download_url(codemeta_download_url)
    if not download_version:
        return result

    latest_version = get_latest_release_version(somef_data)
    if not latest_version:
        return result

    if download_version != latest_version:
        result["has_pitfall"] = True
        result["download_url"] = codemeta_download_url
        result["download_version"] = download_version
        result["latest_release_version"] = latest_version
        result["source"] = codemeta_source

    return result