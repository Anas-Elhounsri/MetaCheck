from typing import Dict
from metacheck.utils.pitfall_utils import extract_metadata_source_filename


def is_repository_url(url: str) -> bool:
    """
    Check if URL appears to be a code repository rather than homepage.
    """
    if not url:
        return False

    url_lower = url.lower()

    # Valid repository indicators
    repo_indicators = [
        'github.com/',
        'gitlab.com/',
        'bitbucket.org/',
        'sourceforge.net/projects/',
        'git.',
        '.git'
    ]

    for indicator in repo_indicators:
        if indicator in url_lower:
            return True

    return False


def is_homepage_url_repo(url: str) -> bool:
    """
    Check if URL appears to be a homepage rather than code repository.
    """
    if not url:
        return False

    url_lower = url.lower()

    # Homepage indicators
    homepage_indicators = [
        '.org/',
        '.com/',
        '.net/',
        '.io/',
        'www.',
        'docs.',
        'documentation',
        'readthedocs',
        'github.io'
    ]

    # If it's clearly a repository URL, it's not a homepage
    if is_repository_url(url):
        return False

    # Check for homepage indicators
    for indicator in homepage_indicators:
        if indicator in url_lower:
            return True

    return False


def detect_coderepository_homepage_pitfall(somef_data: Dict, file_name: str) -> Dict:
    """
    Detect when code repository in metadata files points to homepage instead of repository.
    """
    result = {
        "has_pitfall": False,
        "file_name": file_name,
        "repository_url": None,
        "source": None,
        "metadata_source_file": None,
        "is_homepage": False
    }

    if "code_repository" not in somef_data:
        return result

    repo_entries = somef_data["code_repository"]
    if not isinstance(repo_entries, list):
        return result

    metadata_sources = ["codemeta.json", "DESCRIPTION", "composer.json", "package.json", "pom.xml", "pyproject.toml", "requirements.txt", "setup.py"]

    for entry in repo_entries:
        technique = entry.get("technique", "")
        source = entry.get("source", "")

        is_metadata_source = (
                technique in metadata_sources or
                any(src in source.lower() for src in metadata_sources)
        )

        if is_metadata_source:
            if "result" in entry and "value" in entry["result"]:
                repo_url = entry["result"]["value"]

                if is_homepage_url_repo(repo_url):
                    result["has_pitfall"] = True
                    result["repository_url"] = repo_url
                    result["source"] = source if source else f"technique: {technique}"
                    result["metadata_source_file"] = extract_metadata_source_filename(source)
                    result["is_homepage"] = True
                    break

    return result