from typing import Dict
import re


def is_valid_identifier(identifier: str) -> bool:
    """
    Check if identifier appears to be a valid unique identifier (DOI, URL) rather than a name.
    """
    if not identifier or not isinstance(identifier, str):
        return False

    identifier = identifier.strip()

    if not identifier:
        return False

    # Check for DOI patterns
    doi_patterns = [
        r'^doi:10\.\d+/.+',  # doi:10.xxxx/yyyy format
        r'^10\.\d+/.+'  # 10.xxxx/yyyy format (bare DOI)
    ]

    for pattern in doi_patterns:
        if re.match(pattern, identifier, re.IGNORECASE):
            return True

    # Check for incomplete DOI patterns that should be invalid
    if identifier.lower() in ['doi:', '10.']:
        return False

    # Check for valid URL patterns (http/https only)
    url_pattern = r'^https?://.+'
    if re.match(url_pattern, identifier, re.IGNORECASE):
        return True

    # Check if it looks like a name (contains spaces and common name patterns)
    if ' ' in identifier and not any(char in identifier for char in ['/', ':', '.']):
        return False

    # If it's a single word without special characters, might be a name
    if identifier.replace(' ', '').replace('-', '').replace('_', '').isalpha():
        return False

    return True


def detect_identifier_name_warning(somef_data: Dict, file_name: str) -> Dict:
    """
    Detect when codemeta.json identifier is a name instead of a valid unique identifier,
    but an identifier exists elsewhere.
    """
    result = {
        "has_warning": False,
        "file_name": file_name,
        "codemeta_identifier": None,
        "other_identifier": None,
        "codemeta_source": None,
        "other_source": None
    }

    if "identifier" not in somef_data:
        return result

    identifier_entries = somef_data["identifier"]
    if not isinstance(identifier_entries, list):
        return result

    codemeta_identifier = None
    codemeta_source = None
    other_identifier = None
    other_source = None

    # Look for codemeta identifier (use first one found)
    for entry in identifier_entries:
        source = entry.get("source", "")
        technique = entry.get("technique", "")

        if technique == "code_parser" and "codemeta.json" in source.lower():
            if "result" in entry and "value" in entry["result"]:
                if codemeta_identifier is None:  # Use first one found
                    codemeta_identifier = entry["result"]["value"]
                    codemeta_source = source
                    break  # Stop at first codemeta identifier

    # Look for other valid identifiers
    for entry in identifier_entries:
        source = entry.get("source", "")
        technique = entry.get("technique", "")

        # Skip codemeta entries
        if technique == "code_parser" and "codemeta.json" in source.lower():
            continue

        if "result" in entry and "value" in entry["result"]:
            identifier_value = entry["result"]["value"]

            if is_valid_identifier(identifier_value):
                other_identifier = identifier_value
                other_source = source
                break

    result["codemeta_identifier"] = codemeta_identifier
    result["codemeta_source"] = codemeta_source
    result["other_identifier"] = other_identifier
    result["other_source"] = other_source

    # Warning if codemeta has invalid identifier but valid one exists elsewhere
    if (codemeta_identifier and
            not is_valid_identifier(codemeta_identifier) and
            other_identifier):
        result["has_warning"] = True

    return result