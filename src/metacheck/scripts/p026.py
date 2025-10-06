from typing import Dict
import re
from urllib.parse import urlparse


def normalize_repository_url(url: str) -> str:
    """
    Normalize repository URL for comparison.
    """
    if not url:
        return ""

    url = url.lower().strip()

    url = re.sub(r'^git\+', '', url)  # Remove git+ prefix
    url = re.sub(r'\.git$', '', url)  # Remove .git suffix
    url = re.sub(r'/$', '', url)  # Remove trailing slash

    # Convert SSH to HTTPS format for comparison
    if url.startswith('git@'):
        # Convert git@github.com:user/repo to https://github.com/user/repo
        url = re.sub(r'^git@([^:]+):', r'https://\1/', url)

    return url


def detect_different_repository_pitfall(somef_data: Dict, file_name: str) -> Dict:
    """
    Detect when metadata file codeRepository doesn't point to the same repository as GitHub API.
    """
    result = {
        "has_pitfall": False,
        "file_name": file_name,
        "github_api_url": None,
        "metadata_urls": [],
        "different_urls": []
    }

    if "code_repository" not in somef_data:
        return result

    repo_entries = somef_data["code_repository"]
    if not isinstance(repo_entries, list):
        return result

    github_api_url = None
    metadata_urls = []

    for entry in repo_entries:
        technique = entry.get("technique", "")
        source = entry.get("source", "")

        if "result" in entry and "value" in entry["result"]:
            repo_url = entry["result"]["value"]

            if technique == "GitHub_API":
                github_api_url = repo_url
            elif any(src in source.lower() for src in ["codemeta.json"]):
                metadata_urls.append({
                    "url": repo_url,
                    "source": source,
                    "technique": technique
                })

    if not github_api_url or not metadata_urls:
        return result

    normalized_github_url = normalize_repository_url(github_api_url)

    different_urls = []
    for metadata_entry in metadata_urls:
        normalized_metadata_url = normalize_repository_url(metadata_entry["url"])

        if normalized_github_url != normalized_metadata_url:
            different_urls.append(metadata_entry)

    if different_urls:
        result["has_pitfall"] = True
        result["github_api_url"] = github_api_url
        result["metadata_urls"] = metadata_urls
        result["different_urls"] = different_urls

    return result