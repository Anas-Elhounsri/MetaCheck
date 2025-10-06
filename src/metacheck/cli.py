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
        help="SoMEF confidence threshold (default: 0.8)."
    )

    args = parser.parse_args()
    input_value = args.input
    threshold = args.threshold
    pitfalls_output_dir = args.pitfalls_output
    analysis_output_file = args.analysis_output

    somef_output_dir = os.path.join(os.getcwd(), "somef_outputs")

    if not input_value:
        input_value = input("Enter a GitHub repository URL or path to a JSON file: ").strip()

    if os.path.exists(input_value) and input_value.lower().endswith(".json"):
        print(f"Batch mode: reading repositories from {input_value}")
        success = run_somef_batch(input_value, somef_output_dir, threshold)
        if success:
            run_analysis(somef_output_dir, pitfalls_output_dir, analysis_output_file)
    else:
        print(f"Single repository mode: running SoMEF on {input_value}")
        result_dir = run_somef_single(input_value, somef_output_dir, threshold)
        if result_dir:
            run_analysis(result_dir, pitfalls_output_dir, analysis_output_file)

if __name__ == "__main__":
    cli()
