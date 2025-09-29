from typing import Dict, List
import re
from typing import Dict, List
import re


def is_valid_identifier(identifier: str) -> bool:
    """
    Check if an identifier is a valid unique identifier (DOI, URL, etc.)
    """
    if not identifier:
        return False

    identifier_lower = identifier.lower()

    # Valid identifier patterns
    valid_patterns = [
        r'doi:',
        r'10\.\d+/',  # DOI pattern
        r'https?://'  # URL
    ]

    for pattern in valid_patterns:
        if re.search(pattern, identifier_lower):
            return True

    return False


def has_doi_in_other_sources(identifier_entries: List[Dict]) -> bool:
    """
    Check if there's a DOI in other sources besides codemeta.json
    """
    for entry in identifier_entries:
        if "result" in entry and "value" in entry["result"]:
            identifier_value = entry["result"]["value"]
            source = entry.get("source", "")

            if "codemeta.json" not in source:
                if "doi" in identifier_value.lower() or re.search(r'10\.\d+/', identifier_value):
                    return True

    return False


def detect_identifier_name_warning(somef_data: Dict, file_name: str) -> Dict:
    """
    Detect when codemeta.json identifier is a name instead of valid unique identifier,
    but a valid identifier exists elsewhere.
    """
    result = {
        "has_warning": False,
        "file_name": file_name,
        "codemeta_identifier": None,
        "codemeta_source": None,
        "has_valid_identifier_elsewhere": False,
        "other_identifiers": []
    }

    if "identifier" not in somef_data:
        return result

    identifier_entries = somef_data["identifier"]
    if not isinstance(identifier_entries, list):
        return result

    codemeta_identifier = None
    codemeta_source = None
    other_identifiers = []

    for entry in identifier_entries:
        source = entry.get("source", "")
        technique = entry.get("technique", "")

        if "result" in entry and "value" in entry["result"]:
            identifier_value = entry["result"]["value"]

            if "codemeta.json" in source or (technique == "code_parser" and "codemeta" in source.lower()):
                codemeta_identifier = identifier_value
                codemeta_source = source
            else:
                other_identifiers.append({
                    "value": identifier_value,
                    "source": source,
                    "technique": technique
                })

    if codemeta_identifier and not is_valid_identifier(codemeta_identifier):
        has_valid_elsewhere = False
        for other_id in other_identifiers:
            if is_valid_identifier(other_id["value"]):
                has_valid_elsewhere = True
                break

        has_doi_elsewhere = has_doi_in_other_sources(identifier_entries)

        if has_valid_elsewhere or has_doi_elsewhere:
            result["has_warning"] = True
            result["codemeta_identifier"] = codemeta_identifier
            result["codemeta_source"] = codemeta_source
            result["has_valid_identifier_elsewhere"] = True
            result["other_identifiers"] = other_identifiers

    return result