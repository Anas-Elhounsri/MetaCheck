import os
import json
import subprocess

def run_somef(repo_url, output_file, threshold):
    """Run SoMEF on a given repository and save results."""
    try:
        subprocess.run(
            ["somef", "describe", "-r", repo_url, "-o", output_file, "-t", str(threshold)],
            check=True
        )
        print(f"SoMEF finished for: {repo_url}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running SoMEF for {repo_url}: {e}")
        return False

def run_somef_single(repo_url, output_dir="somef_outputs", threshold=0.8):
    """Run SoMEF for a single repository."""
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "output_1.json")

    print(f"Running SoMEF for {repo_url}...")
    success = run_somef(repo_url, output_file, threshold)
    return output_dir if success else None

def run_somef_batch(json_file, output_dir="somef_outputs", threshold=0.8):
    """Run SoMEF for all repositories listed in a JSON file, then run analysis once."""
    os.makedirs(output_dir, exist_ok=True)

    with open(json_file, "r") as f:
        data = json.load(f)

    # Expected structure: {"repositories": ["repo1", "repo2", ...]}
    repos = data.get("repositories", [])
    if not repos:
        print("No repositories found in JSON file.")
        return False

    print(f"Found {len(repos)} repositories to process.\n")

    for idx, repo_url in enumerate(repos, start=1):
        output_file = os.path.join(output_dir, f"output_{idx}.json")
        print(f"[{idx}/{len(repos)}] Running SoMEF for: {repo_url}")
        run_somef(repo_url, output_file, threshold)

    print("\nFinished running SoMEF for all repositories.")
    return True
