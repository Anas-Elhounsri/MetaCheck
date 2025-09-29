from typing import Dict, List, Tuple, Optional
from utils.pitfall_utils import extract_metadata_source_filename


def extract_requirements_from_metadata(somef_data: Dict) -> Optional[Dict]:
    """
    Extract requirements from metadata files in SoMEF output.
    Returns a dict with source, requirements info, or None if not found.
    """
    if "requirements" not in somef_data:
        return None

    requirements_entries = somef_data["requirements"]
    if not isinstance(requirements_entries, list):
        return None

    metadata_sources = ["codemeta.json", "DESCRIPTION", "composer.json", "package.json", "pom.xml", "pyproject.toml",
                        "requirements.txt", "setup.py"]

    for entry in requirements_entries:
        if "source" in entry:
            source = entry["source"]
            if any(meta_file in source for meta_file in metadata_sources):
                if "result" in entry:
                    return {
                        "source": source,
                        "requirement": entry["result"]
                    }

    return None


def check_requirement_has_version(requirement: Dict) -> bool:
    """
    Check if a single requirement has version information.
    Returns True if version is present and non-empty, False otherwise.
    """
    if "version" in requirement:
        version = requirement["version"]
        # Version should be non-empty string
        if isinstance(version, str) and version.strip():
            return True

    if "value" in requirement:
        value = requirement["value"]
        if isinstance(value, str):

            version_operators = ["==", ">=", "<=", ">", "<", "~=", "!=", "^", "~"]
            if any(op in value for op in version_operators):
                return True

    return False


def analyze_requirements_versions(requirements_data: Dict) -> Tuple[int, int, List[str]]:
    """
    Analyze requirements to count versioned vs unversioned dependencies.
    Returns (total_requirements, unversioned_count, unversioned_names).
    """
    requirement = requirements_data["requirement"]

    if isinstance(requirement, dict):
        requirements_list = [requirement]
    elif isinstance(requirement, list):
        requirements_list = requirement
    else:
        return 0, 0, []

    total_requirements = len(requirements_list)
    unversioned_count = 0
    unversioned_names = []

    for req in requirements_list:
        if isinstance(req, dict):
            has_version = check_requirement_has_version(req)
            if not has_version:
                unversioned_count += 1
                req_name = req.get("name", req.get("value", "unknown"))
                unversioned_names.append(req_name)

    return total_requirements, unversioned_count, unversioned_names


def detect_unversioned_requirements(somef_data: Dict, file_name: str) -> Dict:
    """
    Detect unversioned requirements warning for a single repository.
    Returns detection result with warning info.
    """
    result = {
        "has_warning": False,
        "file_name": file_name,
        "metadata_source": None,
        "metadata_source_file": None,
        "total_requirements": 0,
        "unversioned_count": 0,
        "unversioned_requirements": [],
        "percentage_unversioned": 0.0
    }

    requirements_data = extract_requirements_from_metadata(somef_data)

    if not requirements_data:
        return result

    result["metadata_source"] = requirements_data["source"]

    total_reqs, unversioned_count, unversioned_names = analyze_requirements_versions(requirements_data)

    result["total_requirements"] = total_reqs
    result["unversioned_count"] = unversioned_count
    result["unversioned_requirements"] = unversioned_names
    result["metadata_source_file"] = extract_metadata_source_filename(requirements_data["source"])

    if total_reqs > 0:
        result["percentage_unversioned"] = round((unversioned_count / total_reqs) * 100, 2)

        if unversioned_count > 0:
            result["has_warning"] = True

    return result