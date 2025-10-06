from metacheck.detect_pitfalls_main import main

def run_analysis(input_dir):
    """Run metadata analysis using existing code."""
    print(f"\nRunning analysis on {input_dir}...")
    main(input_dir)
