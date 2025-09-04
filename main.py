from detect_pitfalls import PitfallAnalyzer

def main():
    """Main function to run the pitfall analysis."""
    analyzer = PitfallAnalyzer()

    try:
        # Analyze all repositories
        results = analyzer.analyze_all_repositories()

        # Print summary
        print("\n" + "=" * 60)
        print("REPOSITORY PITFALL ANALYSIS SUMMARY")
        print("=" * 60)

        # LICENSE Analysis Summary
        print("\nLICENSE TEMPLATE PLACEHOLDERS:")
        print(f"  Total repositories: {results['total_repositories_found']}")
        print(f"  Repositories with LICENSE files: {results['license_analysis']['repositories_with_license']}")
        print(
            f"  Repositories with LICENSE placeholders: {results['license_analysis']['repositories_with_license_placeholders']}")
        print(
            f"  Percentage with LICENSE placeholder pitfalls: {results['license_analysis']['percentage_with_license_placeholders']}%")

        print(f"\nLICENSE COPYRIGHT-ONLY:")
        print(f"  Repositories with LICENSE files: {results['license_analysis']['repositories_with_license']}")
        print(
            f"  Repositories with copyright-only LICENSE: {results['license_analysis']['repositories_with_license_copyright_only']}")
        print(
            f"  Percentage with LICENSE copyright-only pitfalls: {results['license_analysis']['percentage_with_license_copyright_only']}%")

        # codemeta Analysis Summary
        print(f"\nCODEMETA SOFTWARE REQUIREMENTS WITHOUT VERSIONS:")
        print(f"  Repositories with codemeta.json: {results['codemeta_analysis']['repositories_with_codemeta']}")
        print(f"  Repositories with software requirements: {results['codemeta_analysis']['repositories_with_software_requirements']}")
        print(f"  Repositories with missing version info: {results['codemeta_analysis']['repositories_with_software_requirements_without_versions']}")
        print(f"  Percentage with codemeta pitfalls: {results['codemeta_analysis']['percentage_with_software_requirements_without_versions']}%")

        print(f"\nCODEMETA SOFTWARE REQUIREMENTS WITH LOCAL FILE URLS:")
        print(f"  Repositories with software requirements: {results['codemeta_analysis']['repositories_with_software_requirements']}")
        print(f"  Repositories with local file URLs: {results['codemeta_analysis']['repositories_with_software_requirements_with_local_file_urls']}")
        print(f"  Percentage with local file URL pitfalls: {results['codemeta_analysis']['percentage_with_software_requirements_with_local_file_urls']}%")

        print(f"\nCODEMETA SOFTWARE REQUIREMENTS WITH HOMEPAGE URLS:")
        print(f"  Repositories with software requirements: {results['codemeta_analysis']['repositories_with_software_requirements']}")
        print(f"  Repositories with homepage URLs: {results['codemeta_analysis']['repositories_with_software_requirements_with_homepage_urls']}")
        print(f"  Percentage with homepage URL pitfalls: {results['codemeta_analysis']['percentage_with_software_requirements_with_homepage_urls']}%")

        print(f"\nCODEMETA PROGRAMMING LANGUAGES WITHOUT VERSIONS:")
        print(f"  Repositories with programming languages: {results['codemeta_analysis']['repositories_with_programming_languages']}")
        print(f"  Repositories with missing version info: {results['codemeta_analysis']['repositories_with_programming_languages_without_versions']}")
        print(f"  Percentage with programming language pitfalls: {results['codemeta_analysis']['percentage_with_programming_languages_without_versions']}%")

        print(f"\nCODEMETA EMPTY IDENTIFIER:")
        print(f"  Repositories with identifier property: {results['codemeta_analysis']['repositories_with_identifier']}")
        print(f"  Repositories with empty identifier: {results['codemeta_analysis']['repositories_with_empty_identifier']}")
        print(f"  Percentage with identifier pitfalls: {results['codemeta_analysis']['percentage_with_empty_identifier']}%")

        print(f"\nCODEMETA KEYWORDS AS STRING:")
        print(f"  Repositories with keywords property: {results['codemeta_analysis']['repositories_with_keywords']}")
        print(f"  Repositories with keywords as string: {results['codemeta_analysis']['repositories_with_keywords_as_string']}")
        print(f"  Percentage with keywords pitfalls: {results['codemeta_analysis']['percentage_with_keywords_as_string']}%")

        print(f"\nCODEMETA CODE REPOSITORY POINTING TO HOMEPAGE:")
        print(f"  Repositories with code repository property: {results['codemeta_analysis']['repositories_with_code_repository']}")
        print(f"  Repositories pointing to homepage: {results['codemeta_analysis']['repositories_with_code_repository_pointing_to_homepage']}")
        print(f"  Percentage with code repository pitfalls: {results['codemeta_analysis']['percentage_with_code_repository_pointing_to_homepage']}%")

        print(f"\nCODEMETA README POINTING TO NON-README:")
        print(f"  Repositories with README property: {results['codemeta_analysis']['repositories_with_readme_property']}")
        print(f"  Repositories with README pointing to non-README: {results['codemeta_analysis']['repositories_with_readme_pointing_to_non_readme']}")
        print(f"  Percentage with README pitfalls: {results['codemeta_analysis']['percentage_with_readme_pointing_to_non_readme']}%")

        print(f"\nCODEMETA LICENSE POINTING TO LOCAL FILE:")
        print(f"  Repositories with license property: {results['codemeta_analysis']['repositories_with_license_property']}")
        print(f"  Repositories with license pointing to local file: {results['codemeta_analysis']['repositories_with_license_pointing_to_local_file']}")
        print(f"  Percentage with license pitfalls: {results['codemeta_analysis']['percentage_with_license_pointing_to_local_file']}%")

        print(f"\nCODEMETA SOFTWARE VERSION AS BRANCH NAME:")
        print(f"  Repositories with software version: {results['codemeta_analysis']['repositories_with_software_version']}")
        print(f"  Repositories with version as branch name: {results['codemeta_analysis']['repositories_with_software_version_as_branch']}")
        print(f"  Percentage with version pitfalls: {results['codemeta_analysis']['percentage_with_software_version_as_branch']}%")

        # Save results to JSON
        analyzer.save_results_to_json(results)

    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Please ensure the 'temp_analysis' directory exists and contains repository subdirectories.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()