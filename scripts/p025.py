from typing import Dict
import re


def detect_license_no_version_pitfall(somef_data: Dict, file_name: str) -> Dict:
    """
    Detect when license from metadata files doesn't have specific version.
    """
    result = {
        "has_pitfall": False,
        "file_name": file_name,
        "license_value": None,
        "source": None
    }

    if "license" not in somef_data:
        return result

    license_entries = somef_data["license"]
    if not isinstance(license_entries, list):
        return result

    metadata_sources = ["codemeta.json", "DESCRIPTION", "composer.json", "package.json", "pom.xml", "pyproject.toml",
                        "requirements.txt", "setup.py"]

    versioned_licenses = {
        "GPL": r"GPL-?\d+(\.\d+)?",
        "LGPL": r"LGPL-?\d+(\.\d+)?",
        "AGPL": r"AGPL-?\d+(\.\d+)?",
        "Apache": r"Apache-?\d+(\.\d+)?",
        "CC": r"CC[- ]BY[- ]?\d+(\.\d+)?",
        "BSD": r"BSD-?\d+[- ]Clause"
    }

    for entry in license_entries:
        source = entry.get("source", "")
        technique = entry.get("technique", "")

        is_metadata_source = (
                technique == "code_parser" and
                any(src in source for src in metadata_sources)
        )

        if is_metadata_source:
            if "result" in entry and "value" in entry["result"]:
                license_value = entry["result"]["value"]

                if isinstance(license_value, str):
                    license_upper = license_value.upper()

                    for license_name, version_pattern in versioned_licenses.items():
                        if license_name in license_upper:
                            if not re.search(version_pattern, license_upper):
                                result["has_pitfall"] = True
                                result["license_value"] = license_value
                                result["source"] = source
                                break

    return result