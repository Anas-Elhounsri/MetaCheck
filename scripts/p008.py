from typing import Dict
import re


def is_local_file_license(license_value: str) -> bool:
    """
    Check if license value points to a local file instead of stating the license name.
    """
    if not license_value:
        return False

    license_lower = license_value.lower()

    # Local file indicators
    local_file_patterns = [
        r'^\./',  # Starts with ./
        r'^\.\./',  # Starts with ../
        r'license\.md$',  # Ends with license.md
        r'license\.txt$',  # Ends with license.txt
        r'license$',  # Just "LICENSE" or "license"
        r'/license',  # Contains /license
        r'\.md$',  # Any .md file
        r'\.txt$'  # Any .txt file
    ]

    for pattern in local_file_patterns:
        if re.search(pattern, license_lower):
            return True

    if license_value.startswith('./') or license_value.startswith('../'):
        return True

    if '/' in license_value or '\\' in license_value:
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

        # Check if it's from a metadata source
        if technique == "code_parser" or any(src in source.lower() for src in metadata_sources):
            if "result" in entry and "value" in entry["result"]:
                license_value = entry["result"]["value"]

                if is_local_file_license(license_value):
                    result["has_pitfall"] = True
                    result["license_value"] = license_value
                    result["source"] = source if source else f"technique: {technique}"
                    result["is_local_file"] = True
                    break

    return result