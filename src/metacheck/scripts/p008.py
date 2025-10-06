from typing import Dict
import re
from metacheck.utils.pitfall_utils import extract_metadata_source_filename

def is_local_file_license(license_value: str) -> bool:
    """
    Check if license value points to a local file instead of stating the license name.
    """
    if not license_value:
        return False

    license_lower = license_value.lower()

    valid_license_patterns = [
        r'https?://spdx\.org/licenses/',  # SPDX license URLs
        r'https?://opensource\.org/licenses/',  # OSI license URLs
        r'https?://www\.gnu\.org/licenses/',  # GNU license URLs
        r'https?://creativecommons\.org/licenses/',  # Creative Commons URLs
        r'https?://www\.apache\.org/licenses/',  # Apache license URLs
        r'https?://www\.mozilla\.org/en-US/MPL/',  # Mozilla license URLs
        r'https?://unlicense\.org',  # Unlicense URL
        r'https?://choosealicense\.com/',  # GitHub's license chooser
    ]

    for pattern in valid_license_patterns:
        if re.search(pattern, license_value, re.IGNORECASE):
            return False

    # Local file indicators
    local_file_patterns = [
        r'^\./',  # Starts with ./
        r'^\.\./',  # Starts with ../
        r'^license\.md$',  # Exactly "license.md"
        r'^license\.txt$',  # Exactly "license.txt"
        r'^license$',  # Exactly "LICENSE" or "license"
        r'^copying$',  # Exactly "COPYING" or "copying"
        r'^copyright$',  # Exactly "COPYRIGHT" or "copyright"
        r'\.md$',  # Any .md file that's not a URL
        r'\.txt$',  # Any .txt file that's not a URL
        r'\.rst$',  # Any .rst file
    ]

    # Check if it starts with relative path indicators
    if license_value.startswith('./') or license_value.startswith('../'):
        return True

    # Check if it contains path separators (likely a file path)
    if ('/' in license_value or '\\' in license_value) and not license_value.startswith('http'):
        return True

    # Check against local file patterns
    for pattern in local_file_patterns:
        if re.search(pattern, license_lower):
            return True

    # Check for common license file names
    license_file_names = [
        'license', 'license.md', 'license.txt', 'license.rst',
        'copying', 'copying.md', 'copying.txt',
        'copyright', 'copyright.md', 'copyright.txt',
        'licence', 'licence.md', 'licence.txt'  # British spelling
    ]

    if license_lower in license_file_names:
        return True

    return False


def detect_local_file_license_pitfall(somef_data: Dict, file_name: str) -> Dict:
    """
    Detect when license in metadata files points to a local file instead of stating the name.
    """
    result = {
        "has_pitfall": False,
        "file_name": file_name,
        "license_value": None,
        "source": None,
        "metadata_source_file": None,
        "is_local_file": False
    }

    if "license" not in somef_data:
        return result

    license_entries = somef_data["license"]
    if not isinstance(license_entries, list):
        return result

    metadata_sources = ["codemeta.json", "DESCRIPTION", "composer.json", "package.json", "pom.xml", "pyproject.toml", "requirements.txt", "setup.py"]

    for entry in license_entries:
        technique = entry.get("technique", "")
        source = entry.get("source", "")

        if technique == "code_parser" or any(src in source.lower() for src in metadata_sources):
            if "result" in entry and "value" in entry["result"]:
                license_value = entry["result"]["value"]

                if is_local_file_license(license_value):
                    result["has_pitfall"] = True
                    result["license_value"] = license_value
                    result["source"] = source if source else f"technique: {technique}"
                    result["metadata_source_file"] = extract_metadata_source_filename(source)
                    result["is_local_file"] = True
                    break

    return result