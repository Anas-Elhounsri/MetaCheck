import argparse
from metacheck.detect_pitfalls_main import main

def cli():
    parser = argparse.ArgumentParser(description="Detect metadata pitfalls in software repositories.")
    parser.add_argument("--input", help="Path to SoMEF output directory", default=None)
    args = parser.parse_args()
    main(args.input)

if __name__ == "__main__":
    cli()
