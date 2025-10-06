# Research Software MetaCheck (a Pitfall/Warning Detection Tool)

This project provides an automated tool for detecting common metadata quality issues (pitfalls & Warnings)
in software repositories. The tool analyzes SoMEF (Software Metadata Extraction Framework) output 
files to identify various problems in repository metadata
files such as `codemeta.json`, `package.json`, `setup.py`, `DESCRIPTION`, and others.

## Overview

MetaCheck identifies **27 different types of metadata quality issues** across multiple programming languages 
(Python, Java, C++, C, R, Rust). These pitfalls range from version mismatches and 
license template placeholders to broken URLs and improperly formatted metadata fields.

### Supported Pitfall Types

The tool detects the following categories of issues:

- **Version-related pitfalls**: Version mismatches between metadata files and releases
- **License-related pitfalls**: Template placeholders, copyright-only licenses, missing version specifications
- **URL validation pitfalls**: Broken links for CI, software requirements, download URLs
- **Metadata format pitfalls**: Improper field formatting, multiple authors in single fields, etc...
- **Identifier pitfalls**: Invalid or missing unique identifiers, bare DOIs
- **Repository reference pitfalls**: Mismatched code repositories, Git shorthand usage

## Requirements

- **Python 3.10**
- Required Python packages:
  - `requests` (for URL validation)
  - `pathlib` (built-in)
  - `json` (built-in)
  - `re` (built-in)
  - `somef` (For extracting metadata from the repositories)

## Setup and Usage

### 1. Prepare SoMEF Output Files

You first need to run:
`pip install git+https://github.com/Anas-Elhounsri/RsMetaCheck.git
`
  
Then run `somef configure` and add you GitHub authentication token which will be used by somef 
to extract the metadata, you can still not include an authentication token and still use SOMEF. 
However, you may be limited to a series of requests per hour depending on the batch size of 
repositories you want to analyze.

### 2. Directory Structure [NEEDS AND UPDATE]
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

After a successful setup, execute the package from the command line if you want to analyze one repository:

`python -m metacheck.cli --input https://github.com/tidyverse/tidyverse  
`
  
or if you wish to analyze in batches, you to run

`python -m metacheck.cli --input repositories.json
`
  
where repositories.json in this case is the **PATH** to the JSON file of your choice that contains 
a list of repositories, and it needs to be structured like the following:

```json
{
  "repositories": [
    "https://gitlab.com/example/example_repo_1",
    "https://gitlab.com/example/example_repo_2",
    "https://github.com/example/example_repo_3"
  ]
}
```


### 4. Output

The tool will:
- Process all JSON files in the `somef_outputs` (by default created by the tool) directory
- Display progress messages showing detected pitfalls
- Generate JSON-LD files of detailed Pitfalls and Warnings detected by the tool in  `output_1_pitfalls.jsonld`, 
`output_2_pitfalls.jsonld`, etc... in `pitfalls` (by default created by the tool) directory
- Generate a comprehensive report in `all_pitfalls_results.json`

The output file contains:
- EVERSE standardized JSON-LD output of each repository
- Summary statistics of analyzed repositories
- Count and percentage for each pitfall type
- Language-specific breakdown for repositories with target languages


## Troubleshooting

### Common Issues

1. **"There is no valid repository URL" error**: Ensure the JSON file that contains the repositories 
has a valid structure and that you are inputing the correct path
2. **Network timeouts**: Some pitfalls validate URLs and may time out—this is normal behavior

### Performance Notes

- URL validation pitfalls may take longer due to network requests
- Large datasets may require several minutes to complete analysis
- Progress is displayed in real-time showing which pitfalls are found

## Contributing

The system is designed with modularity in mind. Each pitfall detector is implemented as a 
separate module in the `scripts/` directory, making it easy to add new pitfall types or modify 
existing detection logic.
