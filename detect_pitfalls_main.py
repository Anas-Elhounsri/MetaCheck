import json
from pathlib import Path

from pitfall_utils import extract_programming_languages
from scripts.p001 import detect_version_mismatch
from scripts.p002 import detect_license_template_placeholders
from scripts.p003 import detect_unversioned_requirements
from scripts.p004 import detect_outdated_datemodified
from scripts.p005 import detect_multiple_authors_single_field_pitfall
from scripts.p006 import detect_readme_homepage_pitfall
from scripts.p007 import detect_reference_publication_archive_pitfall
from scripts.p008 import detect_local_file_license_pitfall
from scripts.p013 import detect_multiple_requirements_string_pitfall
from scripts.p014 import detect_invalid_software_requirement_pitfall
from scripts.p015 import detect_identifier_name_pitfall
from scripts.p017 import detect_empty_identifier_pitfall
from scripts.p019 import detect_coderepository_homepage_pitfall
from scripts.p020 import detect_copyright_only_license
from scripts.p021 import detect_issue_tracker_format_pitfall
from scripts.p022 import detect_outdated_download_url_pitfall
from scripts.p023 import detect_development_status_url_pitfall
from scripts.p026 import detect_git_remote_shorthand_pitfall
from scripts.p027 import detect_bare_doi_pitfall
from scripts.p028 import detect_ci_404_pitfall
from scripts.p030 import detect_different_repository_pitfall
from scripts.p031 import detect_codemeta_version_mismatch_pitfall
from scripts.p032 import detect_raw_swhid_pitfall
from scripts.p011 import detect_programming_language_no_version_pitfall
from scripts.p012 import detect_citation_missing_reference_publication_pitfall
from scripts.p024 import detect_author_name_list_pitfall
from scripts.p025 import detect_license_no_version_pitfall


def detect_all_pitfalls(directory_path: str, output_file: str):
    """
    Detect all software repository pitfalls in SoMEF output files using modular detectors.
    """
    directory = Path(directory_path)

    if not directory.exists():
        print(f"Error: Directory {directory_path} does not exist.")
        return

    results = {
        "summary": {
            "total_repositories_analyzed": 0,
            "repositories_with_target_languages": 0,
            "target_languages": ["Python", "Java", "C++", "C", "R", "Rust"]
        },
        "pitfalls": [
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
                "pitfall_code": "P003",
                "pitfall_desc": "Software requirements in metadata files don't have version specifications",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P004",
                "pitfall_desc": "The dateModified in codemeta.json is outdated compared to the actual repository last update date",
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
                "pitfall_code": "P011",
                "pitfall_desc": "Programming languages in codemeta.json do not have versions",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P012",
                "pitfall_desc": "CITATION.cff does not have referencePublication even though it's referenced in codemeta.json",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P013",
                "pitfall_desc": "The metadata file softwareRequirements have more than one req, but it's written as one string",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P014",
                "pitfall_desc": "The metadata file softwareRequirement points to an invalid page",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P015",
                "pitfall_desc": "codemeta.json Identifier is a name instead of a valid unique identifier, but an identifier exist",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P017",
                "pitfall_desc": "codemeta.json Identifier is empty",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P019",
                "pitfall_desc": "The metadata file coderepository points to their homepage",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P020",
                "pitfall_desc": "LICENSE file only contains copyright information without actual license terms",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P021",
                "pitfall_desc": "codemeta.json IssueTracker violates the expected URL format",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P022",
                "pitfall_desc": "codemeta.json downloadURL is outdated",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P023",
                "pitfall_desc": "codemeta.json developmentStatus is a URL instead of a string",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P024",
                "pitfall_desc": "The metadata file GivenName is a list instead of a string",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P025",
                "pitfall_desc": "The metadata file License does not have the specific version",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P026",
                "pitfall_desc": "The metadata file codeRepository uses Git remote-style shorthand instead of full URL",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P027",
                "pitfall_desc": "codemeta.json uses bare DOIs in the identifier field instead of full https://doi.org/ URL",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P028",
                "pitfall_desc": "In codemeta.json contIntegration link returns 404",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P030",
                "pitfall_desc": "The metadata file codeRepository does not point to the same repository",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P031",
                "pitfall_desc": "codemeta.json version does not match the package's",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            },
            {
                "pitfall_code": "P032",
                "pitfall_desc": "codemeta.json Identifier uses raw SWHIDs without their resolvable URL",
                "count": 0,
                "percentage": 0.0,
                "languages": {}
            }
        ]
    }

    total_repos = 0
    repos_with_target_languages = 0
    pitfall_counts = [0] * 27

    pitfall_detectors = [
        (detect_version_mismatch, "P001"),
        (detect_license_template_placeholders, "P002"),
        (detect_unversioned_requirements, "P003"),
        (detect_outdated_datemodified, "P004"),
        (detect_multiple_authors_single_field_pitfall, "P005"),
        (detect_readme_homepage_pitfall, "P006"),
        (detect_reference_publication_archive_pitfall, "P007"),
        (detect_local_file_license_pitfall, "P008"),
        (detect_programming_language_no_version_pitfall, "P011"),
        (detect_citation_missing_reference_publication_pitfall, "P012"),
        (detect_multiple_requirements_string_pitfall, "P013"),
        (detect_invalid_software_requirement_pitfall, "P014"),
        (detect_identifier_name_pitfall, "P015"),
        (detect_empty_identifier_pitfall, "P017"),
        (detect_coderepository_homepage_pitfall, "P019"),
        (detect_copyright_only_license, "P020"),
        (detect_issue_tracker_format_pitfall, "P021"),
        (detect_outdated_download_url_pitfall, "P022"),
        (detect_development_status_url_pitfall, "P023"),
        (detect_author_name_list_pitfall, "P024"),
        (detect_license_no_version_pitfall, "P025"),
        (detect_git_remote_shorthand_pitfall, "P026"),
        (detect_bare_doi_pitfall, "P027"),
        (detect_ci_404_pitfall, "P028"),
        (detect_different_repository_pitfall, "P030"),
        (detect_codemeta_version_mismatch_pitfall, "P031"),
        (detect_raw_swhid_pitfall, "P032")
    ]

    for json_file in directory.glob("*.json"):
        total_repos += 1

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                somef_data = json.load(f)

            languages = extract_programming_languages(somef_data)

            if languages:
                repos_with_target_languages += 1

            for idx, (detector_func, pitfall_code) in enumerate(pitfall_detectors):
                try:
                    pitfall_result = detector_func(somef_data, json_file.name)

                    if pitfall_result["has_pitfall"]:
                        pitfall_counts[idx] += 1

                        if languages:
                            for lang in languages:
                                if lang in results["pitfalls"][idx]["languages"]:
                                    results["pitfalls"][idx]["languages"][lang] += 1
                                else:
                                    results["pitfalls"][idx]["languages"][lang] = 1

                        print(f"{pitfall_code} - Pitfall found in {json_file.name}")

                except Exception as e:
                    print(f"Error running {pitfall_code} detector on {json_file.name}: {e}")
                    continue

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file {json_file}: {e}")
            continue
        except Exception as e:
            print(f"Error processing file {json_file}: {e}")
            continue

    results["summary"]["total_repositories_analyzed"] = total_repos
    results["summary"]["repositories_with_target_languages"] = repos_with_target_languages

    for i, count in enumerate(pitfall_counts):
        results["pitfalls"][i]["count"] = count
        if total_repos > 0:
            results["pitfalls"][i]["percentage"] = round((count / total_repos) * 100, 2)

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n=== PITFALL DETECTION COMPLETE ===")
        print(f"Total repositories analyzed: {total_repos}")
        print(f"Repositories with target languages: {repos_with_target_languages}")

        for i, (_, pitfall_code) in enumerate(pitfall_detectors):
            print(f"{pitfall_code}: {pitfall_counts[i]} ({results['pitfalls'][i]['percentage']}%)")

        print(f"Results saved to: {output_file}")

    except Exception as e:
        print(f"Error writing output file: {e}")


def main():
    """
    Main function to run all pitfall detections.
    """
    script_dir = Path(__file__).parent

    somef_directory = script_dir / ("somef_output")

    output_file = script_dir / "all_pitfalls_results.json"

    if not somef_directory.exists():
        print(f"Error: Expected directory 'somef_outputs' not found at: {somef_directory}")
        print("Please ensure the 'somef_outputs' directory exists in the same location as this script.")
        return

    detect_all_pitfalls(str(somef_directory), str(output_file))


if __name__ == "__main__":
    main()