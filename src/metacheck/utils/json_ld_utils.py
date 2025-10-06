import json
from datetime import datetime
from typing import Dict, List
from pathlib import Path


def extract_software_info_from_somef(somef_data: Dict) -> Dict:
    """
    Extract software information from SoMEF data for the assessedSoftware section.
    """
    software_info = {
        "@type": "schema:SoftwareApplication",
        "name": "Unknown",
        "softwareVersion": "Unknown",
        "url": "Unknown"
    }

    if "full_name" in somef_data:
        for entry in somef_data["full_name"]:
            if "result" in entry and "value" in entry["result"]:
                software_info["name"] = entry["result"]["value"]
                break

    if "releases" in somef_data:
        releases = somef_data["releases"]
        if isinstance(releases, list) and len(releases) > 0:
            latest_release = releases[0]
            if isinstance(latest_release, dict):
                if "tag" in latest_release:
                    software_info["softwareVersion"] = latest_release["tag"]
                elif "result" in latest_release and isinstance(latest_release["result"], dict):
                    if "tag" in latest_release["result"]:
                        software_info["softwareVersion"] = latest_release["result"]["tag"]

    if "code_repository" in somef_data:
        for entry in somef_data["code_repository"]:
            if "result" in entry and "value" in entry["result"]:
                software_info["url"] = entry["result"]["value"]
                break

    if "identifier" in somef_data:
        for entry in somef_data["identifier"]:
            if "result" in entry and "value" in entry["result"]:
                identifier_value = entry["result"]["value"]
                if identifier_value.startswith("https://doi.org/"):
                    software_info["schema:identifier"] = {"@id": identifier_value}
                elif identifier_value.startswith("10."):
                    software_info["schema:identifier"] = {"@id": f"https://doi.org/{identifier_value}"}
                break

    return software_info


def get_pitfall_description(pitfall_code: str) -> str:
    """
    Get the description for a given pitfall code.
    """
    pitfall_descriptions = {
        "P001": "The metadata file (codemeta or other) has a version which does not correspond to the version used in the latest release",
        "P002": "LICENSE file contains template placeholders like <program>, <year>, <name of author> that were not replaced",
        "W003": "The metadata file (codemeta or other) Software requirements don't have version specifications",
        "W004": "codemeta.json dateModified is outdated compared to the actual repository last update date",
        "P005": "The metadata file (codemeta or other) have multiple authors in single field instead of a list",
        "P006": "In codemeta.json README property pointing to their homepage/wiki instead of README file",
        "P007": "codemeta.json referencePublication refers to software archive instead of paper",
        "P008": "The metadata file (codemeta or other) has License pointing to a local file instead of stating the name",
        "W010": "Programming languages in codemeta.json do not have versions",
        "P011": "CITATION.cff does not have referencePublication even though it's referenced in codemeta.json",
        "W012": "The metadata file (codemeta or other) softwareRequirements have more than one req, but it's written as one string",
        "P013": "The metadata file (codemeta or other) softwareRequirement points to an invalid page",
        "W014": "codemeta.json Identifier is a name instead of a valid unique identifier, but an identifier exist",
        "W015": "codemeta.json Identifier is empty",
        "P016": "The metadata file (codemeta or other) coderepository points to their homepage",
        "P017": "LICENSE file only contains copyright information without actual license terms",
        "P018": "codemeta.json IssueTracker violates the expected URL format",
        "P019": "codemeta.json downloadURL is outdated",
        "P020": "codemeta.json developmentStatus is a URL instead of a string",
        "W021": "The metadata file (codemeta or other) GivenName is a list instead of a string",
        "P022": "The metadata file (codemeta or other) License does not have the specific version",
        "P023": "The metadata file (codemeta or other) codeRepository uses Git remote-style shorthand instead of full URL",
        "P024": "codemeta.json uses bare DOIs in the identifier field instead of full https://doi.org/ URL",
        "P025": "In codemeta.json contIntegration link returns 404",
        "P026": "The metadata file (codemeta or other) codeRepository does not point to the same repository",
        "P027": "codemeta.json version does not match the package's",
        "P028": "codemeta.json Identifier uses raw SWHIDs without their resolvable URL"
    }

    return pitfall_descriptions.get(pitfall_code, f"Description for {pitfall_code}")


def extract_metadata_source(pitfall_result: Dict) -> str:
    """
    Extract the metadata source from a pitfall result.
    Returns the filename part of the source path, or a default value if not present.
    """
    if 'metadata_source_file' in pitfall_result and pitfall_result['metadata_source_file']:
        return pitfall_result['metadata_source_file']

    # Fallback to the old method
    metadata_source = pitfall_result.get('metadata_source', 'metadata files')
    # Extract just the filename from the source path if it's a full path
    if '/' in metadata_source or '\\' in metadata_source:
        metadata_source = metadata_source.split('/')[-1].split('\\')[-1]
    return metadata_source


def extract_metadata_source_filename(source_path: str) -> str:
    """
    Extract the specific metadata file name from a source path.
    This function is reusable for all pitfall detectors that need to identify metadata sources.

    Args:
        source_path: The full source path from SoMEF data

    Returns:
        The filename (e.g., "DESCRIPTION", "codemeta.json") or "metadata files" as fallback
    """
    if not source_path:
        return "metadata files"

    # Define metadata file patterns to look for
    metadata_files = ["codemeta.json", "DESCRIPTION", "composer.json", "package.json",
                      "pom.xml", "pyproject.toml", "requirements.txt", "setup.py"]

    # Check for exact filename matches first
    for meta_file in metadata_files:
        if meta_file in source_path:
            return meta_file

    # If no specific metadata file found, extract filename from path
    if '/' in source_path or '\\' in source_path:
        filename = source_path.split('/')[-1].split('\\')[-1]
        # Check if the extracted filename is a known metadata file
        if filename in metadata_files or any(
                ext in filename.lower() for ext in ['.json', '.xml', '.yml', '.toml', '.txt']):
            return filename

    return "metadata files"


def format_evidence_text(pitfall_code: str, pitfall_result: Dict) -> str:
    """
    Format evidence text based on pitfall type and result data for ALL pitfalls.
    """
    evidence_base = f"{pitfall_code} detected: "

    if pitfall_code == "P001":
        if "metadata_version" in pitfall_result and "release_version" in pitfall_result:
            metadata_source = extract_metadata_source(pitfall_result)
            metadata_version = pitfall_result.get('metadata_version') or 'unknown'
            release_version = pitfall_result.get('release_version') or 'unknown'
            return f"{evidence_base}{metadata_source} version '{metadata_version}' does not match release version '{release_version}'"

    elif pitfall_code == "P002":
        if pitfall_result.get("placeholders_found"):
            return f"{evidence_base} License file contains unreplaced template placeholders"
        return f"{evidence_base} License file contains template placeholders that were not replaced"

    elif pitfall_code == "W003":
        if "unversioned_requirements" in pitfall_result:
            reqs = pitfall_result["unversioned_requirements"]
            metadata_source = extract_metadata_source(pitfall_result)
            if isinstance(reqs, list) and len(reqs) > 0:
                # Filter out None values and convert to strings
                clean_reqs = [str(req) for req in reqs if req is not None][:3]
                if clean_reqs:
                    req_list = ', '.join(clean_reqs)
                    return f"{evidence_base}{metadata_source} contains software requirements without versions: {req_list}{'...' if len(reqs) > 3 else ''}"
        return f"{evidence_base}Software requirements found without version specifications"

    elif pitfall_code == "W004":
        if "codemeta_date_parsed" in pitfall_result and "github_api_date_parsed" in pitfall_result:
            codemeta_date = pitfall_result.get('codemeta_date_parsed') or 'unknown'
            github_date = pitfall_result.get('github_api_date_parsed') or 'unknown'
            return f"{evidence_base}codemeta.json dateModified '{codemeta_date}' is outdated compared to repository date '{github_date}'"
        return f"{evidence_base}dateModified in codemeta.json is outdated compared to actual repository last update"

    elif pitfall_code == "P005":
        if "author_value" in pitfall_result:
            metadata_source = extract_metadata_source(pitfall_result)
            author_value = pitfall_result.get('author_value') or 'unknown'
            return f"{evidence_base}{metadata_source} Multiple authors found in single field: '{author_value}'"

    elif pitfall_code == "P006":
        if "readme_url" in pitfall_result:
            readme_url = pitfall_result.get('readme_url') or 'unknown URL'
            return f"{evidence_base} codemeta.json README property points to homepage/wiki instead of README file: {readme_url}"

    elif pitfall_code == "P007":
        if "reference_url" in pitfall_result:
            reference_url = pitfall_result.get('reference_url') or 'unknown URL'
            return f"{evidence_base}codemeta.json Reference publication points to software archive instead of paper: {reference_url}"

    elif pitfall_code == "P008":
        if "license_value" in pitfall_result:
            metadata_source = extract_metadata_source(pitfall_result)
            license_value = pitfall_result.get('license_value') or 'unknown'
            return f"{evidence_base}{metadata_source} License points to local file instead of license name: '{license_value}'"

    elif pitfall_code == "W010":
        if "programming_languages_without_version" in pitfall_result:
            langs = pitfall_result["programming_languages_without_version"]
            if isinstance(langs, list) and len(langs) > 0:
                # Filter out None values and convert to strings
                clean_langs = [str(lang) for lang in langs if lang is not None]
                if clean_langs:
                    return f"{evidence_base}codemeta.json Programming languages without versions: {', '.join(clean_langs)}"
        return f"{evidence_base} codemeta.json Programming languages in metadata do not have version specifications"

    elif pitfall_code == "P011":
        return f"{evidence_base}CITATION.cff file exists but does not contain referencePublication while codemeta.json references it"

    elif pitfall_code == "W012":
        if "requirements_string" in pitfall_result:
            metadata_source = extract_metadata_source(pitfall_result)
            requirements_string = pitfall_result.get('requirements_string') or 'unknown'
            return f"{evidence_base}{metadata_source} Multiple requirements written as single string: '{requirements_string}'"

    elif pitfall_code == "P013":
        if "invalid_urls" in pitfall_result:
            invalid_urls = pitfall_result["invalid_urls"]
            if isinstance(invalid_urls, list) and len(invalid_urls) > 0:
                # Handle case where invalid_urls might contain None values or dicts
                urls = []
                for url_info in invalid_urls:
                    if isinstance(url_info, dict) and "url" in url_info and url_info["url"]:
                        urls.append(str(url_info["url"]))
                    elif isinstance(url_info, str) and url_info:
                        urls.append(url_info)

                if urls:
                    metadata_source = extract_metadata_source(pitfall_result)
                    url_list = ', '.join(urls[:3])
                    return f"{evidence_base}{metadata_source} Software requirements contain invalid URLs: {url_list}{'...' if len(urls) > 3 else ''}"
        return f"{evidence_base}Software requirements contain invalid URLs"

    elif pitfall_code == "W014":
        if "codemeta_identifier" in pitfall_result:
            identifier = pitfall_result.get('codemeta_identifier') or 'unknown'
            return f"{evidence_base}codemeta.json Identifier is a name instead of valid unique identifier: '{identifier}'"

    elif pitfall_code == "W015":
        return f"{evidence_base}codemeta.json identifier field is empty or missing"

    elif pitfall_code == "P016":
        if "repository_url" in pitfall_result:
            metadata_source = extract_metadata_source(pitfall_result)
            repository_url = pitfall_result.get('repository_url') or 'unknown URL'
            return f"{evidence_base}{metadata_source} codeRepository points to homepage instead of repository: {repository_url}"

    elif pitfall_code == "P017":
        return f"{evidence_base}LICENSE file only contains copyright information without actual license terms"

    elif pitfall_code == "P018":
        if "issue_url" in pitfall_result:
            issue_url = pitfall_result.get('issue_url') or 'unknown URL'
            return f"{evidence_base}codemeta.json IssueTracker URL violates expected format: {issue_url}"

    elif pitfall_code == "P019":
        if "download_url" in pitfall_result:
            download_url = pitfall_result.get('download_url') or 'unknown URL'
            return f"{evidence_base}codemeta.json downloadURL is outdated or invalid: {download_url}"

    elif pitfall_code == "P020":
        if "development_status" in pitfall_result:
            development_status = pitfall_result.get('development_status') or 'unknown'
            return f"{evidence_base}codemeta.json developmentStatus is a URL instead of status string: {development_status}"

    elif pitfall_code == "W021":
        if "author_value" in pitfall_result:
            metadata_source = extract_metadata_source(pitfall_result)
            author_value = pitfall_result.get('author_value') or 'unknown'
            return f"{evidence_base}{metadata_source} GivenName is a list instead of string: {author_value}"

    elif pitfall_code == "P022":
        if "license_value" in pitfall_result:
            metadata_source = extract_metadata_source(pitfall_result)
            license_value = pitfall_result.get('license_value') or 'unknown'
            return f"{evidence_base}{metadata_source} License does not specify version: '{license_value}'"

    elif pitfall_code == "P023":
        if "repository_url" in pitfall_result:
            metadata_source = extract_metadata_source(pitfall_result)
            repository_url = pitfall_result.get('repository_url') or 'unknown URL'
            return f"{evidence_base}{metadata_source} codeRepository uses Git shorthand instead of full URL: '{repository_url}'"

    elif pitfall_code == "P024":
        if "identifier_value" in pitfall_result:
            identifier_value = pitfall_result.get('identifier_value') or 'unknown'
            return f"{evidence_base}Identifier uses bare DOI instead of full URL: '{identifier_value}'"

    elif pitfall_code == "P025":
        if "ci_url" in pitfall_result:
            status = pitfall_result.get("status_code") or "unknown"
            ci_url = pitfall_result.get('ci_url') or 'unknown URL'
            return f"{evidence_base}codemeta.json Continuous integration URL returns {status}: {ci_url}"

    elif pitfall_code == "P026":
        if "github_api_url" in pitfall_result:
            github_api_url = pitfall_result.get('github_api_url') or 'unknown URL'
            return f"{evidence_base}codeRepository points to different repository: {github_api_url}"

    elif pitfall_code == "P027":
        if "codemeta_version" in pitfall_result:
            codemeta_version = pitfall_result.get('codemeta_version') or 'unknown'
            return f"{evidence_base}codemeta.json version '{codemeta_version}' does not match package version"

    elif pitfall_code == "P028":
        if "identifier_value" in pitfall_result:
            identifier_value = pitfall_result.get('identifier_value') or 'unknown'
            return f"{evidence_base}codemeta Identifier uses raw SWHID without resolvable URL: '{identifier_value}'"

    # Default fallback evidence
    file_name = pitfall_result.get('file_name') or 'unknown file'
    return f"{evidence_base}Issue detected in {file_name}"


def get_pitfall_category(pitfall_code: str) -> str:
    """
    Determine the category for assessesIndicator based on pitfall description.
    Returns 'codemeta', 'metadatafile', or 'license'
    """
    pitfall_descriptions = {
        "P001": "metadatafile",  # metadata file version mismatch
        "P002": "license",  # LICENSE file placeholders
        "W003": "metadatafile",  # metadata file requirements
        "W004": "codemeta",  # codemeta.json dateModified
        "P005": "metadatafile",  # metadata file multiple authors
        "P006": "codemeta",  # codemeta.json README property
        "P007": "codemeta",  # codemeta.json referencePublication
        "P008": "metadatafile",  # metadata file License pointing to local file
        "W010": "codemeta",  # codemeta.json programming languages
        "P011": "codemeta",  # CITATION.cff vs codemeta.json
        "W012": "metadatafile",  # metadata file softwareRequirements
        "P013": "metadatafile",  # metadata file softwareRequirement invalid page
        "W014": "codemeta",  # codemeta.json Identifier name
        "W015": "codemeta",  # codemeta.json Identifier empty
        "P016": "metadatafile",  # metadata file coderepository homepage
        "P017": "license",  # LICENSE file copyright only
        "P018": "codemeta",  # codemeta.json IssueTracker
        "P019": "codemeta",  # codemeta.json downloadURL
        "P020": "codemeta",  # codemeta.json developmentStatus
        "W021": "metadatafile",  # metadata file GivenName list
        "P022": "metadatafile",  # metadata file License version
        "P023": "metadatafile",  # metadata file codeRepository shorthand
        "P024": "codemeta",  # codemeta.json bare DOIs
        "P025": "codemeta",  # codemeta.json contIntegration 404
        "P026": "metadatafile",  # metadata file codeRepository different repo
        "P027": "codemeta",  # codemeta.json version mismatch
        "P028": "codemeta"  # codemeta.json raw SWHIDs
    }

    return pitfall_descriptions.get(pitfall_code, "metadatafile")


def extract_software_info_from_somef(somef_data: Dict) -> Dict:
    """
    Extract software information from SoMEF data for the assessedSoftware section.
    """
    software_info = {
        "@type": "schema:SoftwareApplication",
        "name": "Unknown",
        "softwareVersion": "Unknown",
        "url": "Unknown"
    }

    if "full_name" in somef_data:
        for entry in somef_data["full_name"]:
            if "result" in entry and "value" in entry["result"]:
                software_info["name"] = entry["result"]["value"]
                break

    if "releases" in somef_data:
        releases = somef_data["releases"]
        if isinstance(releases, list) and len(releases) > 0:
            latest_release = releases[0]
            if isinstance(latest_release, dict):
                if "tag" in latest_release:
                    software_info["softwareVersion"] = latest_release["tag"]
                elif "result" in latest_release and isinstance(latest_release["result"], dict):
                    if "tag" in latest_release["result"]:
                        software_info["softwareVersion"] = latest_release["result"]["tag"]

    if "code_repository" in somef_data:
        for entry in somef_data["code_repository"]:
            if "result" in entry and "value" in entry["result"]:
                software_info["url"] = entry["result"]["value"]
                break

    if "identifier" in somef_data:
        for entry in somef_data["identifier"]:
            if "result" in entry and "value" in entry["result"]:
                identifier_value = entry["result"]["value"]
                if identifier_value.startswith("https://doi.org/"):
                    software_info["schema:identifier"] = {"@id": identifier_value}
                elif identifier_value.startswith("10."):
                    software_info["schema:identifier"] = {"@id": f"https://doi.org/{identifier_value}"}
                break

    return software_info

def extract_description_info(somef_data: Dict) -> str:
    """
    Extract description information from SoMEF data.
    """
    if "description" in somef_data:
        for entry in somef_data["description"]:
            if "result" in entry and "value" in entry["result"]:
                return entry["result"]["value"]

    return "Software quality assessment for repository metadata"

def convert_sets_to_lists(obj):
    """
    Recursively convert any sets in the data structure to lists for JSON serialization.
    """
    if isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, dict):
        return {key: convert_sets_to_lists(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_sets_to_lists(item) for item in obj]
    else:
        return obj

def create_pitfall_jsonld(somef_data: Dict, pitfall_results: List[Dict], file_name: str) -> Dict:
    """
    Create a JSON-LD structure for detected pitfalls following the sample format.
    """
    software_info = extract_software_info_from_somef(somef_data)
    description_info = extract_description_info(somef_data)

    jsonld_output = {
        "@context": "https://w3id.org/example/metacheck/0.1.0/",
        "@type": "SoftwareQualityAssessment",
        "name": f"Quality Assessment for {software_info['name']}",
        "description": description_info,
        "creator": {
            "@type": "schema:Person",
            "name": "Anas El Hounsri",
            "email": "a.elhounsri@upm.com"
        },
        "dateCreated": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "license": {"@id: https://opensource.org/license/mit"},
        "assessedSoftware": software_info,
        "checks": []
    }

    for pitfall_result in pitfall_results:
        if pitfall_result.get("has_pitfall", False) or pitfall_result.get("has_warning", False):
            pitfall_code = pitfall_result.get("pitfall_code", "Unknown")
            category = get_pitfall_category(pitfall_code)

            check_result = {
                "@type": "CheckResult",
                "assessesIndicator": {"@id": f"https://w3id.org/example/metacheck/i/indicators/{category}"},
                "checkingSoftware": {
                    "@type": "schema:SoftwareApplication",
                    "name": "metacheck",
                    "@id": "https://w3id.org/example/metacheck/tools/",
                    "softwareVersion": "0.1.0"
                },
                "process": get_pitfall_description(pitfall_code),
                "status": {"@id": "schema:CompletedActionStatus"},
                "checkId":pitfall_code,
                "evidence": format_evidence_text(pitfall_code, pitfall_result),
                "suggestion": ""
            }

            jsonld_output["checks"].append(check_result)

    return jsonld_output


def save_individual_pitfall_jsonld(jsonld_data: Dict, output_dir: Path, file_name: str):
    """
    Save individual JSON-LD file for a repository's pitfalls.
    """
    output_dir.mkdir(exist_ok=True)

    base_name = Path(file_name).stem
    output_file = output_dir / f"{base_name}_pitfalls.jsonld"

    try:
        # Convert any sets to lists before JSON serialization
        serializable_data = convert_sets_to_lists(jsonld_data)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2, ensure_ascii=False)

        return str(output_file)
    except Exception as e:
        print(f"Error saving JSON-LD file {output_file}: {e}")
        return None

