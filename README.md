# Research Software MetaCheck (a Pitfall/Warning Detection Tool)

This project provides an automated tool for detecting common metadata quality issues (pitfalls & Warnings) in software repositories. The tool analyzes SoMEF (Software Metadata Extraction Framework) output files to identify various problems in repository metadata files such as `codemeta.json`, `package.json`, `setup.py`, `DESCRIPTION`, and others.

## Overview

MetaCheck identifies **27 different types of metadata quality issues** across multiple programming languages (Python, Java, C++, C, R, Rust). These pitfalls range from version mismatches and license template placeholders to broken URLs and improperly formatted metadata fields.

### Supported Pitfall Types

The tool detects the following categories of issues:

- **Version-related pitfalls**: Version mismatches between metadata files and releases
- **License-related pitfalls**: Template placeholders, copyright-only licenses, missing version specifications
- **URL validation pitfalls**: Broken links for CI, software requirements, download URLs
- **Metadata format pitfalls**: Improper field formatting, multiple authors in single fields etc...
- **Identifier pitfalls**: Invalid or missing unique identifiers, bare DOIs
- **Repository reference pitfalls**: Mismatched code repositories, Git shorthand usage

## Requirements

- **Python 3.10 or higher**
- Required Python packages:
  - `requests` (for URL validation)
  - `pathlib` (built-in)
  - `json` (built-in)
  - `re` (built-in)

## Setup and Usage

### 1. Prepare SoMEF Output Files

Ensure you have SoMEF output JSON files ready for analysis. These files should be placed in a directory named `somef_outputs` in the same location as the main script.

**Important**: Keep the directory name as `somef_outputs` exactly as shown.

### 2. Directory Structure
```
project/ detect_pitfalls_main.py 
        ├── somef_outputs/ # Directory containing SoMEF JSON files │ 
            ├── repository1.json │ 
            ├── repository2.json │ 
            └── ... 
        ├── scripts/ # Individual pitfall detector modules │ 
            ├── p001.py │ 
            ├── p002.py │ 
            └── ... 
        └── all_pitfalls_results.json # Generated output file

```

### 3. Run the Detection Tool

Execute the main script from the command line:

`python detect_pitfalls_main.py
`

### 4. Output

The tool will:
- Process all JSON files in the `somef_outputs` directory
- Display progress messages showing detected pitfalls
- Generate a comprehensive report in `all_pitfalls_results.json`

The output file contains:
- Summary statistics of analyzed repositories
- Count and percentage for each pitfall type
- Language-specific breakdown for repositories with target languages


## Troubleshooting

### Common Issues

1. **"Directory not found" error**: Ensure the `somef_outputs` directory exists and contains JSON files
3. **JSON parsing errors**: Verify that input files are valid JSON format
4. **Network timeouts**: Some pitfalls (P014, P028) validate URLs and may timeout - this is normal behavior

### Performance Notes

- URL validation pitfalls (P014, P028) may take longer due to network requests
- Large datasets may require several minutes to complete analysis
- Progress is displayed in real-time showing which pitfalls are found

## Contributing

The system is designed with modularity in mind. Each pitfall detector is implemented as a separate module in the `scripts/` directory, making it easy to add new pitfall types or modify existing detection logic.
