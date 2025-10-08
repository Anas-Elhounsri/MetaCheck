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
    """Run SoMEF for all repositories listed in a JSON file."""
    os.makedirs(output_dir, exist_ok=True)

    with open(json_file, "r") as f:
        data = json.load(f)

    repos = data.get("repositories", [])
    if not repos:
        print(f" No repositories found in {json_file}.")
        return False

    base_name = os.path.splitext(os.path.basename(json_file))[0]
    print(f"Running SoMEF for {len(repos)} repositories in {base_name}...")

    for idx, repo_url in enumerate(repos, start=1):
        output_file = os.path.join(output_dir, f"{base_name}_output_{idx}.json")
        print(f"[{idx}/{len(repos)}] {repo_url}")
        run_somef(repo_url, output_file, threshold)

    print(f"Completed SoMEF for {base_name}. Results in {output_dir}")
    return True