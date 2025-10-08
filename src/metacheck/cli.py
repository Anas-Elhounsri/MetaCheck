import argparse
import os
from pathlib import Path
from metacheck.run_somef import run_somef_batch
from metacheck.run_analyzer import run_analysis


def cli():
    parser = argparse.ArgumentParser(description="Detect metadata pitfalls in software repositories using SoMEF.")
    parser.add_argument(
        "--input",
        nargs="+",
        required=True,
        help="One or more JSON files containing repositories (e.g., GitHub, GitLab) OR existing SoMEF output files when using --skip-somef."
    )
    parser.add_argument(
        "--skip-somef",
        action="store_true",
        help="Skip SoMEF execution and analyze existing SoMEF output files directly. --input should point to SoMEF JSON files."
    )
    parser.add_argument(
        "--pitfalls-output",
        default=os.path.join(os.getcwd(), "pitfalls_outputs"),
        help="Directory to store pitfall JSON-LD files (default: ./pitfalls_outputs)."
    )
    parser.add_argument(
        "--analysis-output",
        default=os.path.join(os.getcwd(), "analysis_results.json"),
        help="File path for summary results (default: ./analysis_results.json)."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="SoMEF confidence threshold (default: 0.8). Only used when running SoMEF."
    )

    args = parser.parse_args()

    if args.skip_somef:
        print(f"Skipping SoMEF execution. Analyzing {len(args.input)} existing SoMEF output files...")

        somef_json_paths = []
        for json_path in args.input:
            if not os.path.exists(json_path):
                print(f"Warning: File not found, skipping: {json_path}")
                continue
            somef_json_paths.append(Path(json_path))

        if not somef_json_paths:
            print("Error: No valid SoMEF output files found.")
            return

        print(f"Analyzing {len(somef_json_paths)} SoMEF output files...")
        run_analysis(somef_json_paths, args.pitfalls_output, args.analysis_output)

    else:
        threshold = args.threshold
        somef_output_dir = os.path.join(os.getcwd(), "somef_outputs")

        print(f"Detected {len(args.input)} input files:")
        for json_path in args.input:
            if not os.path.exists(json_path):
                print(f"Skipping missing file: {json_path}")
                continue
            print(f"Processing repositories from {json_path}")
            run_somef_batch(json_path, somef_output_dir, threshold)

        run_analysis(somef_output_dir, args.pitfalls_output, args.analysis_output)


if __name__ == "__main__":
    cli()