from typing import Dict


def has_url_format_violation(url: str) -> bool:
    """
    Check if the issue tracker URL violates the expected format.
    Look for newlines, extra whitespace, or malformed URLs.
    """
    if not url:
        return False

    if '\n' in url or '\r' in url:
        return True

    if url != url.strip():
        return True

    if '  ' in url:
        return True

    return False


def detect_issue_tracker_format_pitfall(somef_data: Dict, file_name: str) -> Dict:
    """
    Detect when codemeta.json IssueTracker violates the expected URL format.
    """
    result = {
        "has_pitfall": False,
        "file_name": file_name,
        "issue_url": None,
        "source": None,
        "format_violation": None
    }

    if "issues_url" not in somef_data:
        return result

    issues_entries = somef_data["issues_url"]
    if not isinstance(issues_entries, list):
        return result

    for entry in issues_entries:
        source = entry.get("source", "")
        technique = entry.get("technique", "")

        if "codemeta.json" in source or (technique == "code_parser" and "codemeta" in source.lower()):
            if "result" in entry and "value" in entry["result"]:
                issue_url = entry["result"]["value"]

                if has_url_format_violation(issue_url):
                    result["has_pitfall"] = True
                    result["issue_url"] = issue_url
                    result["source"] = source

                    # Identify the specific violation
                    if '\n' in issue_url or '\r' in issue_url:
                        result["format_violation"] = "Contains newline characters"
                    elif issue_url != issue_url.strip():
                        result["format_violation"] = "Contains leading/trailing whitespace"
                    elif '  ' in issue_url:
                        result["format_violation"] = "Contains multiple consecutive spaces"

                    break

    return result