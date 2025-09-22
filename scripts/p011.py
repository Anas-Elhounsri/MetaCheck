from typing import Dict


def detect_programming_language_no_version_pitfall(somef_data: Dict, file_name: str) -> Dict:
    """
    Detect when programmingLanguages in codemeta.json do not have versions (version is null).
    """
    result = {
        "has_pitfall": False,
        "file_name": file_name,
        "programming_languages_without_version": [],
        "source": None
    }

    if "programming_languages" not in somef_data:
        return result

    programming_languages_entries = somef_data["programming_languages"]
    if not isinstance(programming_languages_entries, list):
        return result

    for entry in programming_languages_entries:
        source = entry.get("source", "")
        technique = entry.get("technique", "")

        if technique == "code_parser" and "codemeta.json" in source:
            if "result" in entry:
                result_data = entry["result"]
                version = result_data.get("version")

                if version is None:
                    lang_name = result_data.get("name", "Unknown")
                    result["programming_languages_without_version"].append(lang_name)
                    result["source"] = source
                    result["has_pitfall"] = True

    return result