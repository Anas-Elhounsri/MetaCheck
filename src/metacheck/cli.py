import argparse
import os
from metacheck.run_somef import run_somef_single, run_somef_batch
from metacheck.run_analyzer import run_analysis

def cli():
    parser = argparse.ArgumentParser(description="Detect metadata pitfalls in software repositories using SoMEF.")
    parser.add_argument(
        "--input",
        help="Either a single GitHub repo URL or a path to a JSON file containing multiple repos."
    )
    parser.add_argument(
        "--output",
        default="somef_outputs",
        help="Directory to store SoMEF outputs (default: somef_outputs)."
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="SoMEF confidence threshold (default: 0.8)."
    )

    args = parser.parse_args()
    input_value = args.input
    output_dir = args.output
    threshold = args.threshold

    if not input_value:
        input_value = input("Enter a GitHub repository URL or path to a JSON file: ").strip()

    if os.path.isfile(input_value) and input_value.endswith(".json"):
        print(f"Batch mode: reading repositories from {input_value}")
        success = run_somef_batch(input_value, output_dir, threshold)
        if success:
            run_analysis(output_dir)
    else:
        print(f"Single repository mode: running SoMEF on {input_value}")
        result_dir = run_somef_single(input_value, output_dir, threshold)
        if result_dir:
            run_analysis(result_dir)

if __name__ == "__main__":
    cli()
