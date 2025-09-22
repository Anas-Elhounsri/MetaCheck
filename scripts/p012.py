from typing import Dict


def detect_citation_missing_reference_publication_pitfall(somef_data: Dict, file_name: str) -> Dict:
    """
    Detect when CITATION.cff doesn't have referencePublication even though it's referenced in codemeta.json.
    """
    result = {
        "has_pitfall": False,
        "file_name": file_name,
        "codemeta_has_reference": False,
        "citation_cff_has_reference": False,
        "citation_cff_exists": False
    }

    if "reference_publication" not in somef_data:
        return result

    ref_pub_entries = somef_data["reference_publication"]
    if not isinstance(ref_pub_entries, list):
        return result

    # Check if there's a reference publication from codemeta.json
    codemeta_has_ref = False
    citation_cff_has_ref = False
    citation_cff_exists_in_somef = False

    for entry in ref_pub_entries:
        source = entry.get("source", "")
        technique = entry.get("technique", "")

        if technique == "code_parser":
            if "codemeta.json" in source:
                codemeta_has_ref = True
                result["codemeta_has_reference"] = True
            elif "CITATION.cff" in source:
                citation_cff_has_ref = True
                result["citation_cff_has_reference"] = True

    # Check if CITATION.cff exists in the repository by looking for other fields from it
    # We need to check other categories to see if CITATION.cff appears as a source
    citation_cff_sources = ["authors", "title", "description", "version", "license"]

    for category in citation_cff_sources:
        if category in somef_data:
            entries = somef_data[category]
            if isinstance(entries, list):
                for entry in entries:
                    source = entry.get("source", "")
                    if "CITATION.cff" in source:
                        citation_cff_exists_in_somef = True
                        result["citation_cff_exists"] = True
                        break

    if codemeta_has_ref and citation_cff_exists_in_somef and not citation_cff_has_ref:
        result["has_pitfall"] = True

    return result