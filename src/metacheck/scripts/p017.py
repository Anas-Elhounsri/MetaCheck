import re
from typing import Dict, Optional


def extract_license_from_file(somef_data: Dict) -> Optional[Dict[str, str]]:
    """
    Extract license content from LICENSE.md file in SoMEF output.
    Returns a dict with source and content, or None if not found.
    """
    if "license" not in somef_data:
        return None

    license_entries = somef_data["license"]
    if not isinstance(license_entries, list):
        return None

    for entry in license_entries:
        if "source" in entry:
            source = entry["source"]
            if "LICENSE.md" in source:
                if "result" in entry and "value" in entry["result"]:
                    return {
                        "source": source,
                        "content": entry["result"]["value"]
                    }

    return None


def check_copyright_only_license(license_content: str) -> bool:
    """
    Check if license file only contains copyright information without actual license terms.
    Example:
    YEAR: 2017
    COPYRIGHT HOLDER: Adam H. Sparks
    """
    if not license_content:
        return False

    content_lower = license_content.lower()
    content_lines = [line.strip() for line in license_content.strip().split('\n') if line.strip()]

    # Patterns that indicate copyright-only content
    copyright_only_patterns = [
        r'year:\s*\d{4}',  # YEAR: 2017
        r'copyright\s+holder:\s*[a-zA-Z]',  # COPYRIGHT HOLDER: Someone
        r'author:\s*[a-zA-Z]',  # AUTHOR: Someone
        r'copyright\s*©?\s*\d{4}',  # Copyright 2017 or Copyright © 2017
        r'©\s*\d{4}',  # © 2017
        r'\(c\)\s*\d{4}',  # (C) 2017
    ]

    # Patterns that indicate actual license terms
    license_term_patterns = [
        r'permission\s+is\s+hereby\s+granted',
        r'subject\s+to\s+the\s+following\s+conditions',
        r'redistribution\s+and\s+use',
        r'without\s+restriction',
        r'without\s+warranty',
        r'liability',
        r'terms\s+and\s+conditions',
        r'licensed\s+under',
        r'mit\s+license',
        r'apache\s+license',
        r'gnu\s+general\s+public\s+license',
        r'bsd\s+license',
        r'creative\s+commons',
    ]

    has_copyright_info = any(re.search(pattern, content_lower) for pattern in copyright_only_patterns)

    has_license_terms = any(re.search(pattern, content_lower) for pattern in license_term_patterns)

    if has_copyright_info and not has_license_terms and len(content_lines) <= 10:
        return True

    # Special case: check for the exact format "YEAR: xxxx" and "COPYRIGHT HOLDER: xxxx"
    year_pattern_found = bool(re.search(r'year:\s*\d{4}', content_lower))
    copyright_holder_pattern_found = bool(re.search(r'copyright\s+holder:', content_lower))

    if year_pattern_found and copyright_holder_pattern_found:
        return True

    return False


def detect_copyright_only_license(somef_data: Dict, file_name: str) -> Dict:
    """
    Detect copyright-only license pitfall for a single repository.
    Returns detection result with pitfall info or None if no pitfall found.
    """
    result = {
        "has_pitfall": False,
        "file_name": file_name,
        "license_source": None,
        "is_copyright_only": False
    }

    license_info = extract_license_from_file(somef_data)

    if license_info:
        license_content = license_info["content"]
        result["license_source"] = license_info["source"]

        is_copyright_only = check_copyright_only_license(license_content)

        if is_copyright_only:
            result["has_pitfall"] = True
            result["is_copyright_only"] = True

    return result