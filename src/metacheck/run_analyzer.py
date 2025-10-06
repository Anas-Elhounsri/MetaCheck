from metacheck.detect_pitfalls_main import main

def run_analysis(somef_dir, pitfalls_dir, analysis_file):
    """Run metadata analysis using existing code."""
    print(f"\nRunning analysis on {somef_dir}...")
    main(input_dir=somef_dir, pitfalls_dir=pitfalls_dir, analysis_output=analysis_file)
