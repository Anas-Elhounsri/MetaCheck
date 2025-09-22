import re
from typing import Dict, List


def extract_programming_languages(somef_data: Dict) -> List[str]:
    """
    Extract programming languages from SoMEF output, filtering for specific languages only.
    Only includes: Python, Java, C++, C, R, Rust
    """
    target_languages = {"Python", "Java", "C++", "C", "R", "Rust"}

    if "programming_languages" not in somef_data:
        return []

    languages = somef_data["programming_languages"]
    if not isinstance(languages, list):
        return []

    lang_list = []
    seen_languages = set()

    for lang_entry in languages:
        if isinstance(lang_entry, dict) and "result" in lang_entry:
            result = lang_entry["result"]
            if isinstance(result, dict):
                lang_name = None
                if "value" in result:
                    lang_name = result["value"]
                elif "name" in result:
                    lang_name = result["name"]

                if lang_name:
                    normalized_lang = normalize_language_name(lang_name)
                    if normalized_lang in target_languages and normalized_lang not in seen_languages:
                        lang_list.append(normalized_lang)
                        seen_languages.add(normalized_lang)

    return lang_list


def normalize_language_name(lang_name: str) -> str:
    """
    Normalize language names to match target languages.
    """
    lang_name = lang_name.strip()

    if lang_name.lower().startswith("python"):
        return "Python"

    if lang_name.lower() in ["c++", "cpp", "cplusplus"]:
        return "C++"

    target_map = {
        "java": "Java",
        "c": "C",
        "r": "R",
        "rust": "Rust"
    }

    return target_map.get(lang_name.lower(), lang_name)


def normalize_version(version: str) -> str:
    """
    Normalize version string for comparison by removing common prefixes like 'v'.
    """
    if not version:
        return ""

    normalized = re.sub(r'^v', '', version, flags=re.IGNORECASE)
    return normalized.strip()