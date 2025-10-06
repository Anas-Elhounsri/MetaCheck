import json
from pathlib import Path

from metacheck.utils.pitfall_utils import extract_programming_languages
from metacheck.utils.json_ld_utils import create_pitfall_jsonld, save_individual_pitfall_jsonld

# Import all pitfall detectors
from metacheck.scripts.p001 import detect_version_mismatch
from metacheck.scripts.p002 import detect_license_template_placeholders
from metacheck.scripts.w003 import detect_unversioned_requirements
from metacheck.scripts.w004 import detect_outdated_datemodified
from metacheck.scripts.p005 import detect_multiple_authors_single_field_pitfall
from metacheck.scripts.p006 import detect_readme_homepage_pitfall
from metacheck.scripts.p007 import detect_reference_publication_archive_pitfall
from metacheck.scripts.p008 import detect_local_file_license_pitfall
from metacheck.scripts.w010 import detect_programming_language_no_version_pitfall
from metacheck.scripts.p011 import detect_citation_missing_reference_publication_pitfall
from metacheck.scripts.w012 import detect_multiple_requirements_string_warning
from metacheck.scripts.p013 import detect_invalid_software_requirement_pitfall
from metacheck.scripts.w014 import detect_identifier_name_warning
from metacheck.scripts.w015 import detect_empty_identifier_warning
from metacheck.scripts.p016 import detect_coderepository_homepage_pitfall
from metacheck.scripts.p017 import detect_copyright_only_license
from metacheck.scripts.p018 import detect_issue_tracker_format_pitfall
from metacheck.scripts.p019 import detect_outdated_download_url_pitfall
from metacheck.scripts.p020 import detect_development_status_url_pitfall
from metacheck.scripts.w021 import detect_author_name_list_warning
from metacheck.scripts.p022 import detect_license_no_version_pitfall
from metacheck.scripts.p023 import detect_git_remote_shorthand_pitfall
from metacheck.scripts.p024 import detect_bare_doi_pitfall
from metacheck.scripts.p025 import detect_ci_404_pitfall
from metacheck.scripts.p026 import detect_different_repository_pitfall
from metacheck.scripts.p027 import detect_codemeta_version_mismatch_pitfall
from metacheck.scripts.p028 import detect_raw_swhid_pitfall


def detect_all_pitfalls(directory_path: str, pitfalls_output_dir: str, output_file: str):
    """
    Detect all software repository pitfalls in SoMEF output files using modular detectors.
    Now also generates individual JSON-LD files for each repository.
    """

    directory = Path(directory_path)
    pitfalls_output_dir = Path(pitfalls_output_dir)
    pitfalls_output_dir.mkdir(exist_ok=True, parents=True)

    results = {
        "summary": {
            "total_repositories_analyzed": 0,
            "repositories_with_target_languages": 0,
            "individual_jsonld_files_created": 0,
            "total_pitfalls_detected": 0,  # Add this
            "total_warnings_detected": 0,  # Add this
            "target_languages": ["Python", "Java", "C++", "C", "R", "Rust"]

        },
        "pitfalls & warnings": [
            {
                "pitfall_code": "P001",
                "pitfall_desc": "The metadata file (codemeta or other) has a version which does not correspond to the version used in the latest release",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P002",
                "pitfall_desc": "LICENSE file contains template placeholders like <program>, <year>, <name of author> that were not replaced",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "warning_code": "W003",
                "warning_desc": "Software requirements in metadata files don't have version specifications",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "warning_code": "W004",
                "warning_desc": "The dateModified in codemeta.json is outdated compared to the actual repository last update date",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P005",
                "pitfall_desc": "Metadata files have multiple authors in single field instead of a list",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P006",
                "pitfall_desc": "In codemeta.json README property pointing to their homepage/wiki instead of README file",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P007",
                "pitfall_desc": "codemeta.json referencePublication refers to software archive instead of paper",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P008",
                "pitfall_desc": "The metadata file has License pointing to a local file instead of stating the name",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "warning_code": "W010",
                "warning_desc": "Programming languages in codemeta.json do not have versions",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P011",
                "pitfall_desc": "CITATION.cff does not have referencePublication even though it's referenced in codemeta.json",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "warning_code": "W012",
                "warning_desc": "The metadata file softwareRequirements have more than one req, but it's written as one string",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P013",
                "pitfall_desc": "The metadata file softwareRequirement points to an invalid page",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "warning_code": "W014",
                "warning_desc": "codemeta.json Identifier is a name instead of a valid unique identifier, but an identifier exist",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "warning_code": "W015",
                "warning_desc": "codemeta.json Identifier is empty",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P016",
                "pitfall_desc": "The metadata file coderepository points to their homepage",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P017",
                "pitfall_desc": "LICENSE file only contains copyright information without actual license terms",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P018",
                "pitfall_desc": "codemeta.json IssueTracker violates the expected URL format",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P019",
                "pitfall_desc": "codemeta.json downloadURL is outdated",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P020",
                "pitfall_desc": "codemeta.json developmentStatus is a URL instead of a string",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "warning_code": "W021",
                "warning_desc": "The metadata file GivenName is a list instead of a string",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P022",
                "pitfall_desc": "The metadata file License does not have the specific version",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P023",
                "pitfall_desc": "The metadata file codeRepository uses Git remote-style shorthand instead of full URL",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P024",
                "pitfall_desc": "codemeta.json uses bare DOIs in the identifier field instead of full https://doi.org/ URL",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P025",
                "pitfall_desc": "In codemeta.json contIntegration link returns 404",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P026",
                "pitfall_desc": "The metadata file codeRepository does not point to the same repository",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P027",
                "pitfall_desc": "codemeta.json version does not match the package's",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P028",
                "pitfall_desc": "codemeta.json Identifier uses raw SWHIDs without their resolvable URL",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            }
        ]
    }

    total_pitfalls = 0
    total_warnings = 0
    total_repos = 0
    repos_with_target_languages = 0
    jsonld_files_created = 0
    pitfall_counts = [0] * 27

    pitfall_detectors = [
        (detect_version_mismatch, "P001"),
        (detect_license_template_placeholders, "P002"),
        (detect_unversioned_requirements, "W003"),
        (detect_outdated_datemodified, "W004"),
        (detect_multiple_authors_single_field_pitfall, "P005"),
        (detect_readme_homepage_pitfall, "P006"),
        (detect_reference_publication_archive_pitfall, "P007"),
        (detect_local_file_license_pitfall, "P008"),
        (detect_programming_language_no_version_pitfall, "W010"),
        (detect_citation_missing_reference_publication_pitfall, "P011"),
        (detect_multiple_requirements_string_warning, "W012"),
        (detect_invalid_software_requirement_pitfall, "P013"),
        (detect_identifier_name_warning, "W014"),
        (detect_empty_identifier_warning, "W015"),
        (detect_coderepository_homepage_pitfall, "P016"),
        (detect_copyright_only_license, "P017"),
        (detect_issue_tracker_format_pitfall, "P018"),
        (detect_outdated_download_url_pitfall, "P019"),
        (detect_development_status_url_pitfall, "P020"),
        (detect_author_name_list_warning, "W021"),
        (detect_license_no_version_pitfall, "P022"),
        (detect_git_remote_shorthand_pitfall, "P023"),
        (detect_bare_doi_pitfall, "P024"),
        (detect_ci_404_pitfall, "P025"),
        (detect_different_repository_pitfall, "P026"),
        (detect_codemeta_version_mismatch_pitfall, "P027"),
        (detect_raw_swhid_pitfall, "P028")
    ]

    for json_file in directory.glob("*.json"):
        total_repos += 1

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                somef_data = json.load(f)

            languages = extract_programming_languages(somef_data)

            if languages:
                repos_with_target_languages += 1

            repo_pitfall_results = []

            for idx, (detector_func, pitfall_code) in enumerate(pitfall_detectors):
                try:
                    pitfall_result = detector_func(somef_data, json_file.name)

                    pitfall_result["pitfall_code"] = pitfall_code
                    repo_pitfall_results.append(pitfall_result)

                    has_pitfall = pitfall_result.get("has_pitfall", False)
                    has_warning = pitfall_result.get("has_warning", False)
                    has_issue = has_pitfall or has_warning

                    if has_issue:
                        pitfall_counts[idx] += 1

                        if has_pitfall:
                            total_pitfalls += 1
                        if has_warning:
                            total_warnings += 1

                        if languages:
                            for lang in languages:
                                if lang in results["pitfalls & warnings"][idx]["languages"]:
                                    results["pitfalls & warnings"][idx]["languages"][lang] += 1
                                else:
                                    results["pitfalls & warnings"][idx]["languages"][lang] = 1

                        issue_type = "Pitfall" if pitfall_result.get("has_pitfall", False) else "Warning"
                        print(f"{pitfall_code} - {issue_type} found in {json_file.name}")

                except Exception as e:
                    print(f"Error running {pitfall_code} detector on {json_file.name}: {e}")
                    continue

            try:
                has_any_issue = any(
                    result.get("has_pitfall", False) or result.get("has_warning", False)
                    for result in repo_pitfall_results
                )

                if has_any_issue:
                    jsonld_data = create_pitfall_jsonld(somef_data, repo_pitfall_results, json_file.name)
                    saved_file = save_individual_pitfall_jsonld(jsonld_data, pitfalls_output_dir, json_file.name)

                    if saved_file:
                        jsonld_files_created += 1
                        print(f"Created JSON-LD file: {saved_file}")

            except Exception as e:
                print(f"Error creating JSON-LD for {json_file.name}: {e}")


        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file {json_file}: {e}")
            continue
        except Exception as e:
            print(f"Error processing file {json_file}: {e}")
            continue

    results["summary"]["total_repositories_analyzed"] = total_repos
    results["summary"]["repositories_with_target_languages"] = repos_with_target_languages
    results["summary"]["individual_jsonld_files_created"] = jsonld_files_created
    results["summary"]["total_pitfalls_detected"] = total_pitfalls
    results["summary"]["total_warnings_detected"] = total_warnings

    for i, count in enumerate(pitfall_counts):
        results["pitfalls & warnings"][i]["count"] = count
        if total_repos > 0:
            results["pitfalls & warnings"][i]["percentage"] = round((count / total_repos) * 100, 2)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n=== PITFALL/WARNING DETECTION COMPLETE ===")
        print(f"Total repositories analyzed: {total_repos}")
        print(f"Repositories with target languages: {repos_with_target_languages}")
        print(f"Individual JSON-LD files created: {jsonld_files_created}")
        print(f"JSON-LD files saved to: {pitfalls_output_dir}")

        for i, (_, pitfall_code) in enumerate(pitfall_detectors):
            print(f"{pitfall_code}: {pitfall_counts[i]} ({results['pitfalls & warnings'][i]['percentage']}%)")

        print(f"Summary results saved to: {output_file}")

    except Exception as e:
        print(f"Error writing output file: {e}")


def main(input_dir=None, pitfalls_dir=None, analysis_output=None):
    """
    Main function to run all pitfall detections.
    Args:
        input_dir (str, optional): Path to the SoMEF outputs directory.
        pitfalls_dir (str, optional): Path to save individual pitfall JSON-LD files.
        analysis_output (str, optional): Path to save summary results JSON.
    """
    project_root = Path.cwd()
    somef_directory = Path(input_dir) if input_dir else project_root / "somef_outputs"
    pitfalls_directory = Path(pitfalls_dir) if pitfalls_dir else project_root / "pitfalls_outputs"
    output_file = Path(analysis_output) if analysis_output else project_root / "analysis_results.json"

    if not somef_directory.exists():
        print(f"Error: Directory not found: {somef_directory}")
        print("Please ensure the directory exists.")
        return

    detect_all_pitfalls(str(somef_directory), str(pitfalls_directory), str(output_file))


if __name__ == "__main__":
    main()
