import os
import json
import re
from typing import Dict, List, Tuple, Optional, Union
from pathlib import Path


class PitfallAnalyzer:
    """Analyzes repositories for various pitfalls in repositories"""

    def __init__(self, temp_analysis_dir: str = "temp_analysis"):
        self.temp_analysis_dir = Path(temp_analysis_dir)

        # LICENSE-related attributes
        self.license_filenames = ["LICENSE", "LICENSE.txt", "LICENSE.md", "License", "license"]
        self.template_patterns = [
            r"<year>", r"\[year\]",
            r"<name>", r"\[name\]",
            r"<program>", r"\[program\]"
        ]

        self.codemeta_filenames = ["codemeta.json"]

    def _get_repositories(self) -> List[Path]:
        """ Get all subdirectories (repositories) in the temp_analysis folder."""
        if not self.temp_analysis_dir.exists():
            raise FileNotFoundError(f"Directory '{self.temp_analysis_dir}' does not exist")

        return [
            item for item in self.temp_analysis_dir.iterdir()
            if item.is_dir()
        ]

    def _find_file_recursive(self, repo_path: Path, filenames: List[str]) -> Optional[Tuple[Path, Path]]:
        """
        Find file in the repository structure.
        Returns tuple of (file_path, containing_subdirectory) if found.
        """
        # check the repo root
        for filename in filenames:
            file_path = repo_path / filename
            if file_path.is_file():
                return file_path, repo_path

        # If not found in root, search in subdirectories
        try:
            for subdir in repo_path.iterdir():
                if subdir.is_dir():
                    for filename in filenames:
                        file_path = subdir / filename
                        if file_path.is_file():
                            return file_path, subdir

        except PermissionError:
            pass

        return None

    def _read_text_file(self, file_path: Path) -> Dict:
        """Read a text file with multiple encoding fallbacks."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return {"content": file.read()}
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return {"content": file.read()}
            except Exception as e:
                return {"error": f"Failed to read file with latin-1 encoding: {str(e)}"}
        except Exception as e:
            return {"error": f"Failed to read file: {str(e)}"}

    def _read_json_file(self, file_path: Path) -> Dict:
        """Read and parse a JSON file with error handling."""
        try:
            text_result = self._read_text_file(file_path)

            if "error" in text_result:
                return text_result

            text_content = text_result["content"]
            json_data = json.loads(text_content)
            return {"content": json_data}

        except json.JSONDecodeError as e:
            return {"error": f"Invalid JSON format: {str(e)}"}
        except Exception as e:
            return {"error": f"Error reading file: {str(e)}"}

    ########################################## Pitfalls Detection #################################################

    def _has_template_placeholders(self, license_content: str) -> Tuple[bool, List[str]]:
        """ P02: Check if LICENSE content contains template placeholders."""
        found_placeholders = []

        for pattern in self.template_patterns:
            matches = re.findall(pattern, license_content, re.IGNORECASE)
            if matches:
                found_placeholders.extend(matches)

        return bool(found_placeholders), found_placeholders

    def _analyze_software_requirements(self, codemeta_data: Dict) -> Tuple[bool, Dict]:
        """
        Analyze softwareRequirements for missing versions.
        Returns (has_pitfall, analysis_details)

        The pitfall is: having softwareRequirements but some items lack version information.
        """
        analysis = {
            "has_software_requirements": False,
            "total_requirements": 0,
            "requirements_without_version": 0,
            "requirements_with_version": 0,
            "missing_version_items": [],
            "structure_type": "none"
        }

        # Look for softwareRequirements (case variations possible)
        software_reqs = None
        software_reqs_key = None
        for key in codemeta_data.keys():
            if key.lower() in ['softwarerequirements', 'software_requirements']:
                software_reqs = codemeta_data[key]
                software_reqs_key = key
                break

        if not software_reqs:
            return False, analysis

        analysis["has_software_requirements"] = True

        # Handle different structures of softwareRequirements
        if isinstance(software_reqs, list):
            # Structure: softwareRequirements: [...]
            analysis["structure_type"] = "list"
            requirements_list = software_reqs

        elif isinstance(software_reqs, dict):
            # Handling two more structures
            keys = list(software_reqs.keys())
            if any(key.isdigit() or key in ['SystemRequirements'] for key in keys):
                # Structure: softwareRequirements: {"1": {...}, "2": {...}}
                analysis["structure_type"] = "numbered_object"
                requirements_list = []
                for key, value in software_reqs.items():
                    if key != 'SystemRequirements' and value is not None:
                        requirements_list.append(value)
            else:
                # Structure: softwareRequirements: {...} (single requirement)
                analysis["structure_type"] = "single_object"
                requirements_list = [software_reqs]
        else:
            # Structure: softwareRequirements: "string" or other
            analysis["structure_type"] = "string_or_other"
            requirements_list = [software_reqs]

        analysis["total_requirements"] = len(requirements_list)

        for req in requirements_list:
            if isinstance(req, dict):

                has_version = any(key.lower() in ['version', 'softwareversion', 'applicationversion']
                                  for key in req.keys())

                if has_version:
                    analysis["requirements_with_version"] += 1
                else:
                    analysis["requirements_without_version"] += 1
                    name = req.get('name', req.get('identifier', 'Unknown'))
                    analysis["missing_version_items"].append(name)
            elif isinstance(req, str):

                analysis["requirements_without_version"] += 1
                analysis["missing_version_items"].append(req)
            else:
                analysis["requirements_without_version"] += 1
                analysis["missing_version_items"].append(str(req))

        has_pitfall = analysis["requirements_without_version"] > 0
        return has_pitfall, analysis

    def _analyze_software_requirements_local_files(self, codemeta_data: Dict) -> Tuple[bool, Dict]:
        """
        Placeholder method for software requirements local files analysis.
        Returns (has_pitfall, analysis_details)
        """
        analysis = {
            "has_software_requirements": False,
            "total_requirements": 0,
            "local_file_urls": [],
            "structure_type": "none"
        }

        return False, analysis

    def _analyze_readme_property(self, codemeta_data: Dict) -> Tuple[bool, Dict]:
        """
        Analyze README property for pointing to homepage/wiki instead of README file.
        Returns (has_pitfall, analysis_details)

        The pitfall is: having a README property that points to a homepage, wiki, or documentation
        site instead of an actual README file.
        """
        analysis = {
            "has_readme_property": False,
            "readme_url": None,
            "points_to_non_readme": False,
            "detected_type": None
        }

        readme_value = None
        for key in codemeta_data.keys():
            if key.lower() in ['readme', 'readmeurl']:
                readme_value = codemeta_data[key]
                break

        if not readme_value:
            return False, analysis

        analysis["has_readme_property"] = True
        analysis["readme_url"] = readme_value

        if not isinstance(readme_value, str):
            return False, analysis

        # Patterns that indicate non-README URLs
        homepage_patterns = [
            r'\/wiki\/?$',  # ends with /wiki or /wiki/
            r'\/wiki\/[^\/]+',  # contains /wiki/something
            r'github\.io',  # GitHub Pages
            r'readthedocs\.io',  # Read the Docs
            r'\.github\.io',  # GitHub.io sites
            r'\/docs\/?$',  # ends with /docs or /docs/
            r'\/documentation\/?$',  # ends with /documentation
            r'\/home\/?$',  # ends with /home
            r'\/index\.html?$',  # ends with /index.html or /index.htm
            r'\/$'  # just ends with / (likely homepage)
        ]

        # Check for non-README indicators
        for pattern in homepage_patterns:
            if re.search(pattern, readme_value, re.IGNORECASE):
                analysis["points_to_non_readme"] = True
                if 'wiki' in pattern:
                    analysis["detected_type"] = "wiki"
                elif 'github.io' in pattern or 'readthedocs.io' in pattern:
                    analysis["detected_type"] = "documentation_site"
                elif 'docs' in pattern or 'documentation' in pattern:
                    analysis["detected_type"] = "documentation"
                elif pattern == r'\/$':
                    analysis["detected_type"] = "homepage"
                else:
                    analysis["detected_type"] = "non_readme"
                break

        if not analysis["points_to_non_readme"]:
            readme_file_patterns = [
                r'readme\.md$',
                r'readme\.txt$',
                r'readme\.rst$',
                r'readme$',
                r'README\.md$',
                r'README\.txt$',
                r'README\.rst$',
                r'README$'
            ]

            points_to_readme_file = any(
                re.search(pattern, readme_value, re.IGNORECASE)
                for pattern in readme_file_patterns
            )

            if not points_to_readme_file and readme_value.endswith('/'):
                analysis["points_to_non_readme"] = True
                analysis["detected_type"] = "directory"

        has_pitfall = analysis["points_to_non_readme"]
        return has_pitfall, analysis

    def _analyze_license_property(self, codemeta_data: Dict) -> Tuple[bool, Dict]:
        """
        Analyze license property for pointing to local files instead of license names/identifiers.
        Returns (has_pitfall, analysis_details)

        The pitfall is: having a license property that points to a local file (like "LICENSE.md")
        instead of stating the actual license name or SPDX identifier.
        """
        analysis = {
            "has_license_property": False,
            "license_value": None,
            "points_to_local_file": False,
            "detected_filename": None,
            "license_structure": "none"
        }

        license_value = None
        for key in codemeta_data.keys():
            if key.lower() == 'license':
                license_value = codemeta_data[key]
                break

        if not license_value:
            return False, analysis

        analysis["has_license_property"] = True
        analysis["license_value"] = license_value

        license_to_check = None
        if isinstance(license_value, str):
            analysis["license_structure"] = "string"
            license_to_check = license_value

        elif isinstance(license_value, dict):
            analysis["license_structure"] = "object"
            for field in ['identifier', 'name', 'url', '@id']:
                if field in license_value and license_value[field]:
                    license_to_check = license_value[field]
                    break

        elif isinstance(license_value, list):
            analysis["license_structure"] = "array"
            for lic in license_value:
                if isinstance(lic, str):
                    license_to_check = lic
                elif isinstance(lic, dict):
                    for field in ['identifier', 'name', 'url', '@id']:
                        if field in lic and lic[field]:
                            license_to_check = lic[field]
                            break
                if license_to_check:
                    break

        if not license_to_check or not isinstance(license_to_check, str):
            return False, analysis

        # Patterns that indicate local license files
        local_file_patterns = [
            r'^LICENSE$',  # exactly "LICENSE"
            r'^LICENSE\.(md|txt|rst)$',  # LICENSE.md, LICENSE.txt, LICENSE.rst
            r'^License$',  # exactly "License"
            r'^License\.(md|txt|rst)$',  # License.md, License.txt, License.rst
            r'^license$',  # exactly "license"
            r'^license\.(md|txt|rst)$',  # license.md, license.txt, license.rst
            r'^COPYING$',  # exactly "COPYING"
            r'^COPYING\.(md|txt|rst)$',  # COPYING.md, COPYING.txt, COPYING.rst
            r'^LICENCE$',  # exactly "LICENCE" (British spelling)
            r'^LICENCE\.(md|txt|rst)$',  # LICENCE.md, LICENCE.txt, LICENCE.rst
            r'\.\/LICENSE',  # ./LICENSE (relative path)
            r'\.\/License',  # ./License (relative path)
            r'\.\/license',  # ./license (relative path)
            r'^[^\/]*\/LICENSE',  # any_dir/LICENSE
            r'^[^\/]*\/License',  # any_dir/License
            r'^[^\/]*\/license'  # any_dir/license
        ]

        # Check if license points to a local file
        for pattern in local_file_patterns:
            if re.match(pattern, license_to_check, re.IGNORECASE):
                analysis["points_to_local_file"] = True
                analysis["detected_filename"] = license_to_check
                break

        # Additional check: if it's a path-like string (contains ./ or just a filename)
        if not analysis["points_to_local_file"]:
            # Check for other file-like patterns
            if (license_to_check.startswith('./') or
                    license_to_check.startswith('../') or
                    (not license_to_check.startswith('http') and
                     not license_to_check.startswith('https://') and
                     '.' in license_to_check and
                     not license_to_check.startswith('spdx.org') and
                     len(license_to_check.split()) == 1)):  # single word with extension

                # Make sure it's not a valid SPDX URL or license name
                if not any(valid_indicator in license_to_check.lower() for valid_indicator in [
                    'spdx.org', 'apache', 'mit', 'gpl', 'bsd', 'cc0', 'unlicense',
                    'artistic', 'eclipse', 'mozilla', 'zlib', 'isc'
                ]):
                    analysis["points_to_local_file"] = True
                    analysis["detected_filename"] = license_to_check

        has_pitfall = analysis["points_to_local_file"]
        return has_pitfall, analysis

    def _analyze_software_version(self, codemeta_data: Dict) -> Tuple[bool, Dict]:
        """
        Analyze softwareVersion for branch names instead of proper version numbers.
        Returns (has_pitfall, analysis_details)

        The pitfall is: having a softwareVersion that uses branch names (like "master", "main", "develop")
        instead of proper semantic versions or release tags.
        """
        analysis = {
            "has_software_version": False,
            "software_version": None,
            "is_branch_name": False,
            "detected_branch_type": None
        }

        software_version = None
        for key in codemeta_data.keys():
            if key.lower() in ['softwareversion', 'software_version', 'version']:
                software_version = codemeta_data[key]
                break

        if not software_version:
            return False, analysis

        analysis["has_software_version"] = True
        analysis["software_version"] = software_version

        if not isinstance(software_version, str):
            return False, analysis

        # Patterns that indicate branch names instead of version numbers
        branch_name_patterns = [
            # Main branches
            (r'^master$', 'main_branch'),
            (r'^main$', 'main_branch'),
            (r'^trunk$', 'main_branch'),

            # Development branches
            (r'^develop$', 'development_branch'),
            (r'^development$', 'development_branch'),
            (r'^dev$', 'development_branch'),
            (r'^devel$', 'development_branch'),

            # Feature/topic branches
            (r'^feature.*', 'feature_branch'),
            (r'^feat.*', 'feature_branch'),
            (r'^topic.*', 'topic_branch'),
            (r'^fix.*', 'fix_branch'),
            (r'^bugfix.*', 'fix_branch'),
            (r'^hotfix.*', 'fix_branch'),

            # Release branches
            (r'^release.*', 'release_branch'),
            (r'^rel.*', 'release_branch'),

            # Other common branch patterns
            (r'^stable$', 'stable_branch'),
            (r'^latest$', 'latest_branch'),
            (r'^current$', 'current_branch'),
            (r'^head$', 'head_branch'),
            (r'^tip$', 'tip_branch'),

            # Branch-like patterns with slashes
            (r'.*\/.*', 'path_like_branch'),
        ]

        version_lower = software_version.lower().strip()
        for pattern, branch_type in branch_name_patterns:
            if re.match(pattern, version_lower, re.IGNORECASE):
                analysis["is_branch_name"] = True
                analysis["detected_branch_type"] = branch_type
                break

        if not analysis["is_branch_name"]:
            # Check if it doesn't look like a proper semantic version or tag
            # Proper versions typically have numbers and dots, like "1.0.0", "v2.1", "2023.1"
            proper_version_patterns = [
                r'^\d+\.\d+(\.\d+)?',  # semantic versions: 1.0, 1.0.0, 1.2.3
                r'^v\d+\.\d+(\.\d+)?',  # tagged versions: v1.0, v1.0.0
                r'^\d+\.\d+\.\d+(-\w+)?$',  # semantic with pre-release: 1.0.0-alpha
                r'^\d{4}\.\d{1,2}(\.\d+)?$',  # date-based: 2023.1, 2023.12.1
                r'^\d+[a-zA-Z]\d*$',  # versions like 1a2, 2b1
                r'^\d+(\.\d+)*[a-zA-Z]\d*$',  # versions like 1.0a1, 2.1b3
            ]

            is_proper_version = any(
                re.match(pattern, software_version)
                for pattern in proper_version_patterns
            )

            # If it doesn't match proper version patterns and contains only letters/underscores/dashes
            # it might be a branch name
            if not is_proper_version and re.match(r'^[a-zA-Z_-]+$', software_version):
                analysis["is_branch_name"] = True
                analysis["detected_branch_type"] = "custom_branch"

        has_pitfall = analysis["is_branch_name"]
        return has_pitfall, analysis

    def _analyze_license_copyright_only(self, license_content: str) -> Tuple[bool, Dict]:
        """
        Analyze LICENSE file for copyright-only content without actual license terms.
        Returns (has_pitfall, analysis_details)

        The pitfall is: having a LICENSE file that only contains copyright information
        but no actual license terms or permissions.
        """
        analysis = {
            "has_copyright_info": False,
            "has_license_terms": False,
            "copyright_patterns_found": [],
            "license_indicators_found": [],
            "content_type": "unknown",
            "estimated_content_categories": []
        }

        if not license_content or not license_content.strip():
            analysis["content_type"] = "empty"
            return False, analysis

        content_lower = license_content.lower()
        content_lines = license_content.strip().split('\n')

        # Patterns that indicate copyright information
        copyright_patterns = [
            r'copyright\s+\(c\)\s+\d{4}',  # Copyright (C) 2017
            r'copyright\s+©\s+\d{4}',      # Copyright © 2017
            r'copyright\s+\d{4}',          # Copyright 2017
            r'©\s+\d{4}',                  # © 2017
            r'\(c\)\s+\d{4}',              # (C) 2017
            r'year:\s*\d{4}',              # YEAR: 2017 or YEAR:2017
            r'copyright\s+holder:\s*[a-zA-Z]',  # COPYRIGHT HOLDER: Someone
            r'author:\s*[a-zA-Z]',         # AUTHOR: Someone
        ]

        # Patterns that indicate actual license terms
        license_term_patterns = [
            # Common license identifiers
            r'mit\s+license',
            r'apache\s+license',
            r'gnu\s+general\s+public\s+license',
            r'bsd\s+license',
            r'creative\s+commons',
            r'mozilla\s+public\s+license',

            # License permissions/terms keywords
            r'permission\s+is\s+hereby\s+granted',
            r'subject\s+to\s+the\s+following\s+conditions',
            r'redistribution\s+and\s+use',
            r'without\s+restriction',
            r'including\s+without\s+limitation',
            r'as\s+is\s+basis',
            r'without\s+warranty',
            r'liable\s+for\s+any\s+damages',
            r'terms\s+and\s+conditions',
            r'you\s+may\s+not\s+use\s+this\s+file\s+except',
            r'licensed\s+under',
            r'this\s+license',
            r'the\s+above\s+copyright\s+notice',

            # SPDX identifiers
            r'spdx-license-identifier',
            r'apache-2\.0',
            r'mit',
            r'gpl-[23]\.0',
            r'bsd-[23]-clause',
            r'cc0-1\.0',

            # Legal terms
            r'disclaimer\s+of\s+warranty',
            r'limitation\s+of\s+liability',
            r'use\s+is\s+subject\s+to\s+license\s+terms',
            r'all\s+rights\s+reserved',
            r'granted\s+to\s+you\s+under',
            r'permission\s+to\s+use',
            r'permission\s+to\s+modify',
            r'permission\s+to\s+distribute',
        ]

        for pattern in copyright_patterns:
            matches = re.findall(pattern, content_lower)
            if matches:
                analysis["has_copyright_info"] = True
                analysis["copyright_patterns_found"].extend(matches)

        for pattern in license_term_patterns:
            if re.search(pattern, content_lower):
                analysis["has_license_terms"] = True
                analysis["license_indicators_found"].append(pattern.replace('\\s+', ' ').replace('\\', ''))

        non_empty_lines = len([line for line in content_lines if line.strip()])

        # Estimate content type based on various factors
        if non_empty_lines <= 5:
            if analysis["has_copyright_info"] and not analysis["has_license_terms"]:
                analysis["content_type"] = "copyright_only_short"
                analysis["estimated_content_categories"].append("minimal_copyright_info")
            elif not analysis["has_copyright_info"] and not analysis["has_license_terms"]:
                analysis["content_type"] = "minimal_content"
            else:
                analysis["content_type"] = "short_with_license"
        elif non_empty_lines <= 20:
            if analysis["has_copyright_info"] and not analysis["has_license_terms"]:
                analysis["content_type"] = "copyright_only_medium"
                analysis["estimated_content_categories"].append("extended_copyright_info")
            else:
                analysis["content_type"] = "medium_content"
        else:
            if analysis["has_copyright_info"] and not analysis["has_license_terms"]:
                analysis["content_type"] = "copyright_only_long"
            else:
                analysis["content_type"] = "full_license"

        # Additional content analysis
        if 'year:' in content_lower and 'copyright holder:' in content_lower:
            analysis["estimated_content_categories"].append("template_format")

        if re.search(r'^\s*\d{4}\s*$', content_lower, re.MULTILINE):
            analysis["estimated_content_categories"].append("year_only_line")

        if re.search(r'copyright\s+holder:\s*[a-zA-Z]', content_lower):
            analysis["estimated_content_categories"].append("holder_specified")

        # Check for common copyright-only patterns
        simple_copyright_patterns = [
            r'^\s*copyright\s+\(c\)\s+\d{4}\s+[a-zA-Z\s\.]+\s*$',
            r'^\s*year:\s*\d{4}\s*\n\s*copyright\s+holder:\s+[a-zA-Z\s\.]+\s*$',
            r'^\s*©\s+\d{4}\s+[a-zA-Z\s\.]+\s*$',
        ]

        content_stripped = content_lower.strip()
        for pattern in simple_copyright_patterns:
            if re.match(pattern, content_stripped, re.MULTILINE | re.DOTALL):
                analysis["estimated_content_categories"].append("simple_copyright_statement")
                break

        if analysis["has_copyright_info"]:
            analysis["debug_info"] = {
                "content_lines": len(content_lines),
                "non_empty_lines": non_empty_lines,
                "content_sample": content_lower[:100] if len(content_lower) > 100 else content_lower
            }

        has_pitfall = analysis["has_copyright_info"] and not analysis["has_license_terms"]

        return has_pitfall, analysis

    def analyze_license_pitfalls(self, repo_path: Path) -> Dict:
        """Analyze LICENSE file pitfalls in a repository."""
        repo_name = repo_path.name
        result = {
            "repository": repo_name,
            "has_license": False,
            "license_file": None,
            "license_location": None,
            "has_license_placeholders": False,
            "license_placeholders_found": [],
            "has_license_copyright_only": False,
            "license_copyright_analysis": {}
        }

        license_info = self._find_file_recursive(repo_path, self.license_filenames)
        if not license_info:
            return result

        license_file, license_dir = license_info
        result["has_license"] = True
        result["license_file"] = license_file.name

        relative_location = license_dir.relative_to(repo_path)
        result["license_location"] = str(relative_location) if str(relative_location) != "." else "root"

        try:
            license_content = self._read_text_file(license_file)
            if "error" in license_content:
                result["license_error"] = license_content["error"]
                return result

            content = license_content["content"]

            has_placeholder_pitfall, placeholders = self._has_template_placeholders(content)
            result["has_license_placeholders"] = has_placeholder_pitfall
            result["license_placeholders_found"] = placeholders

            has_copyright_only_pitfall, copyright_analysis = self._analyze_license_copyright_only(content)
            result["has_license_copyright_only"] = has_copyright_only_pitfall
            result["license_copyright_analysis"] = copyright_analysis

        except Exception as e:
            result["license_error"] = str(e)

        return result

    def _analyze_programming_languages_versions(self, codemeta_data: Dict) -> Tuple[bool, Dict]:
        """
        Analyze programmingLanguage for missing version information.
        Returns (has_pitfall, analysis_details)

        The pitfall is: having programmingLanguage entries without version information.
        NOT having programmingLanguage at all is NOT a pitfall.
        """
        analysis = {
            "has_programming_languages": False,
            "total_languages": 0,
            "languages_without_version": 0,
            "languages_with_version": 0,
            "missing_version_items": [],
            "structure_type": "none"
        }

        # Look for programmingLanguage property (case variations possible)
        programming_languages = None
        for key in codemeta_data.keys():
            if key.lower() in ['programminglanguage', 'programming_language', 'programminglanguages']:
                programming_languages = codemeta_data[key]
                break

        if not programming_languages:
            return False, analysis

        analysis["has_programming_languages"] = True

        # Handle different structures
        if isinstance(programming_languages, list):
            analysis["structure_type"] = "list"
            languages_list = programming_languages
        elif isinstance(programming_languages, str):
            analysis["structure_type"] = "string"
            languages_list = [programming_languages]
        elif isinstance(programming_languages, dict):
            analysis["structure_type"] = "object"
            languages_list = [programming_languages]
        else:
            analysis["structure_type"] = "other"
            languages_list = [programming_languages]

        analysis["total_languages"] = len(languages_list)

        for lang in languages_list:
            has_version = False
            lang_name = "Unknown"

            if isinstance(lang, dict):
                # Object format: {"name": "Python", "version": "3.8"}
                lang_name = lang.get('name', lang.get('identifier', 'Unknown'))
                has_version = any(key.lower() in ['version', 'versionrequirement', 'softwareversion']
                                  for key in lang.keys())
            elif isinstance(lang, str):
                # String format - check if it contains version info
                lang_name = lang
                # Patterns that indicate version info in string
                version_patterns = [
                    r'.*\s+\d+\.\d+',  # "Python 3.8"
                    r'.*\s+v\d+\.\d+',  # "Python v3.8"
                    r'.*\s+>=?\s*\d+\.\d+',  # "Python >= 3.8"
                    r'.*\s+\(\d+\.\d+\)',  # "Python (3.8)"
                    r'.*\d+\.\d+.*',  # "Python3.8" or "3.8"
                ]
                has_version = any(re.search(pattern, lang, re.IGNORECASE) for pattern in version_patterns)

            if has_version:
                analysis["languages_with_version"] += 1
            else:
                analysis["languages_without_version"] += 1
                analysis["missing_version_items"].append(lang_name)

        # The pitfall exists if there are languages without version info
        has_pitfall = analysis["languages_without_version"] > 0
        return has_pitfall, analysis

    def _analyze_software_requirements_homepage_urls(self, codemeta_data: Dict) -> Tuple[bool, Dict]:
        """
        Analyze softwareRequirements for URLs pointing to homepages instead of specific packages.
        Returns (has_pitfall, analysis_details)

        The pitfall is: having softwareRequirements that point to homepages/main sites
        instead of specific package repositories or proper package specifications.
        """
        analysis = {
            "has_software_requirements": False,
            "total_requirements": 0,
            "requirements_with_homepage_urls": 0,
            "requirements_with_proper_specs": 0,
            "homepage_url_items": [],
            "structure_type": "none"
        }

        # Look for softwareRequirements
        software_reqs = None
        for key in codemeta_data.keys():
            if key.lower() in ['softwarerequirements', 'software_requirements']:
                software_reqs = codemeta_data[key]
                break

        if not software_reqs:
            return False, analysis

        analysis["has_software_requirements"] = True

        # Handle different structures
        if isinstance(software_reqs, list):
            analysis["structure_type"] = "list"
            requirements_list = software_reqs
        elif isinstance(software_reqs, dict):
            keys = list(software_reqs.keys())
            if any(key.isdigit() or key in ['SystemRequirements'] for key in keys):
                analysis["structure_type"] = "numbered_object"
                requirements_list = []
                for key, value in software_reqs.items():
                    if key != 'SystemRequirements' and value is not None:
                        requirements_list.append(value)
            else:
                analysis["structure_type"] = "single_object"
                requirements_list = [software_reqs]
        else:
            analysis["structure_type"] = "string_or_other"
            requirements_list = [software_reqs]

        analysis["total_requirements"] = len(requirements_list)

        # Patterns that indicate homepage URLs (problematic)
        homepage_url_patterns = [
            # Main homepages and domains
            r'https?://python\.org/?$',
            r'https?://www\.python\.org/?$',
            r'https?://r-project\.org/?$',
            r'https?://www\.r-project\.org/?$',
            r'https?://java\.com/?$',
            r'https?://nodejs\.org/?$',
            r'https?://www\.nodejs\.org/?$',
            r'https?://golang\.org/?$',
            r'https?://go\.dev/?$',
            r'https?://ruby-lang\.org/?$',
            r'https?://www\.ruby-lang\.org/?$',
            r'https?://php\.net/?$',
            r'https?://www\.php\.net/?$',

            # General homepage patterns
            r'https?://[^/]+/?$',  # Just domain with optional trailing slash
            r'https?://www\.[^/]+/?$',  # www.domain.com
            r'https?://[^/]+/index\.html?$',  # domain/index.html
            r'https?://[^/]+/home/?$',  # domain/home
            r'https?://[^/]+/about/?$',  # domain/about

            # Documentation homepages
            r'https?://[^/]+\.readthedocs\.io/?$',  # readthedocs main page
            r'https?://[^/]+\.github\.io/?$',  # github pages main

            # Repository homepages (not specific packages)
            r'https?://github\.com/[^/]+/?$',  # GitHub user/org page
            r'https?://gitlab\.com/[^/]+/?$',  # GitLab user/org page
            r'https?://bitbucket\.org/[^/]+/?$',  # Bitbucket user/org page
            r'https?://github\.com/[^/]+/[^/]+/?$',  # GitHub repo main page (no specific file/release)
            r'https?://gitlab\.com/[^/]+/[^/]+/?$',  # GitLab repo main page
        ]

        for req in requirements_list:
            is_homepage_url = False
            url_to_check = None

            if isinstance(req, str):
                url_to_check = req
            elif isinstance(req, dict):
                for field in ['url', 'downloadUrl', 'codeRepository', 'identifier', '@id']:
                    if field in req and req[field] and isinstance(req[field], str):
                        url_to_check = req[field]
                        break

            if url_to_check and url_to_check.startswith(('http://', 'https://')):
                for pattern in homepage_url_patterns:
                    if re.match(pattern, url_to_check, re.IGNORECASE):
                        is_homepage_url = True
                        analysis["homepage_url_items"].append({
                            "url": url_to_check,
                            "type": "string" if isinstance(req, str) else "object",
                            "matched_pattern": "homepage_url"
                        })
                        break

            if is_homepage_url:
                analysis["requirements_with_homepage_urls"] += 1
            else:
                analysis["requirements_with_proper_specs"] += 1

        has_pitfall = analysis["requirements_with_homepage_urls"] > 0
        return has_pitfall, analysis

    def _analyze_identifier_empty(self, codemeta_data: Dict) -> Tuple[bool, Dict]:
        """
        Analyze identifier property for empty values.
        Returns (has_pitfall, analysis_details)

        The pitfall is: having an identifier property that is empty, null, or contains only whitespace.
        NOT having an identifier property is NOT a pitfall.
        """
        analysis = {
            "has_identifier": False,
            "identifier_value": None,
            "is_empty": False,
            "identifier_type": "none"
        }

        identifier_value = None
        for key in codemeta_data.keys():
            if key.lower() == 'identifier':
                identifier_value = codemeta_data[key]
                break

        if identifier_value is None:
            return False, analysis

        analysis["has_identifier"] = True
        analysis["identifier_value"] = identifier_value

        if isinstance(identifier_value, str):
            analysis["identifier_type"] = "string"

            if not identifier_value or identifier_value.strip() == "":
                analysis["is_empty"] = True
        elif isinstance(identifier_value, list):
            analysis["identifier_type"] = "list"

            if not identifier_value or all(
                    not item or (isinstance(item, str) and item.strip() == "")
                    for item in identifier_value
            ):
                analysis["is_empty"] = True
        elif isinstance(identifier_value, dict):
            analysis["identifier_type"] = "object"

            if not identifier_value or all(
                    not value or (isinstance(value, str) and value.strip() == "")
                    for value in identifier_value.values()
            ):
                analysis["is_empty"] = True
        else:

            analysis["identifier_type"] = "other"
            if identifier_value == "" or identifier_value is None:
                analysis["is_empty"] = True

        has_pitfall = analysis["is_empty"]
        return has_pitfall, analysis

    def _analyze_keywords_string_instead_of_list(self, codemeta_data: Dict) -> Tuple[bool, Dict]:
        """
        Analyze keywords property for string format instead of list format.
        Returns (has_pitfall, analysis_details)

        The pitfall is: having keywords as a string (comma-separated or otherwise)
        instead of an array/list of strings as per CodeMeta specification.
        """
        analysis = {
            "has_keywords": False,
            "keywords_value": None,
            "is_string": False,
            "keywords_type": "none",
            "parsed_keywords": []
        }

        keywords_value = None
        for key in codemeta_data.keys():
            if key.lower() in ['keywords', 'keyword', 'tags', 'tag']:
                keywords_value = codemeta_data[key]
                break

        if keywords_value is None:
            return False, analysis

        analysis["has_keywords"] = True
        analysis["keywords_value"] = keywords_value

        if isinstance(keywords_value, str):
            analysis["keywords_type"] = "string"
            analysis["is_string"] = True

            if ',' in keywords_value:
                analysis["parsed_keywords"] = [k.strip() for k in keywords_value.split(',') if k.strip()]
            elif ';' in keywords_value:
                analysis["parsed_keywords"] = [k.strip() for k in keywords_value.split(';') if k.strip()]
            else:
                analysis["parsed_keywords"] = [keywords_value.strip()] if keywords_value.strip() else []

        elif isinstance(keywords_value, list):
            analysis["keywords_type"] = "list"
            analysis["is_string"] = False  # This is the correct format
        elif isinstance(keywords_value, dict):
            analysis["keywords_type"] = "object"
            analysis["is_string"] = False  # Could be valid depending on structure
        else:
            analysis["keywords_type"] = "other"
            analysis["is_string"] = False

        has_pitfall = analysis["is_string"]
        return has_pitfall, analysis

    def _analyze_code_repository_homepage_url(self, codemeta_data: Dict) -> Tuple[bool, Dict]:
        """
        Analyze codeRepository property for URLs pointing to homepages instead of actual repositories.
        Returns (has_pitfall, analysis_details)

        The pitfall is: having codeRepository point to a homepage, documentation site,
        or general domain instead of the actual code repository.
        """
        analysis = {
            "has_code_repository": False,
            "code_repository_value": None,
            "points_to_homepage": False,
            "detected_type": None
        }

        code_repo_value = None
        for key in codemeta_data.keys():
            if key.lower() in ['coderepository', 'code_repository', 'repository', 'repo']:
                code_repo_value = codemeta_data[key]
                break

        if not code_repo_value:
            return False, analysis

        analysis["has_code_repository"] = True
        analysis["code_repository_value"] = code_repo_value

        if not isinstance(code_repo_value, str):
            return False, analysis

        homepage_patterns = [

            r'https?://[^/]+\.org/?$',  # project.org
            r'https?://www\.[^/]+\.org/?$',  # www.project.org
            r'https?://[^/]+\.com/?$',  # project.com
            r'https?://www\.[^/]+\.com/?$',  # www.project.com
            r'https?://[^/]+\.net/?$',  # project.net
            r'https?://www\.[^/]+\.net/?$',  # www.project.net

            r'https?://[^/]+\.readthedocs\.io/?$',  # readthedocs main page
            r'https?://[^/]+\.github\.io/?$',  # github pages main
            r'https?://docs\.[^/]+/?$',  # docs.project.com
            r'https?://documentation\.[^/]+/?$',  # documentation.project.com

            r'https?://[^/]+/index\.html?$',  # /index.html
            r'https?://[^/]+/home/?$',  # /home
            r'https?://[^/]+/about/?$',  # /about
            r'https?://[^/]+/?$',  # Just domain root

            r'https?://[^/]+\.linkedin\.com/.*',  # LinkedIn profiles
            r'https?://twitter\.com/[^/]+/?$',  # Twitter profiles
            r'https?://[^/]+\.academia\.edu/.*',  # Academia.edu
            r'https?://orcid\.org/.*',  # ORCID profiles

            r'https?://github\.com/[^/]+/?$',  # GitHub user/org page (no specific repo)
            r'https?://gitlab\.com/[^/]+/?$',  # GitLab user/org page
            r'https?://bitbucket\.org/[^/]+/?$',  # Bitbucket user/org page
        ]

        # Check for homepage patterns
        for pattern in homepage_patterns:
            if re.match(pattern, code_repo_value, re.IGNORECASE):
                analysis["points_to_homepage"] = True
                if 'readthedocs' in pattern or 'docs' in pattern or 'documentation' in pattern:
                    analysis["detected_type"] = "documentation_site"
                elif 'github.io' in pattern:
                    analysis["detected_type"] = "github_pages"
                elif any(social in pattern for social in ['linkedin', 'twitter', 'academia', 'orcid']):
                    analysis["detected_type"] = "social_profile"
                elif '/home' in pattern or '/about' in pattern or '/index' in pattern:
                    analysis["detected_type"] = "homepage_page"
                elif pattern.endswith('/?$'):
                    analysis["detected_type"] = "domain_root"
                else:
                    analysis["detected_type"] = "homepage"
                break

        if not analysis["points_to_homepage"]:
            valid_repo_patterns = [
                r'https?://github\.com/[^/]+/[^/]+',  # GitHub repo
                r'https?://gitlab\.com/[^/]+/[^/]+',  # GitLab repo
                r'https?://.*\.git$',  # .git URLs
                r'git@.*:.*',  # SSH git URLs
            ]

            is_valid_repo = any(re.match(pattern, code_repo_value, re.IGNORECASE)
                                for pattern in valid_repo_patterns)

            if not is_valid_repo and code_repo_value.startswith(('http://', 'https://')):
                # If it's a URL but doesn't match valid repo patterns, might be homepage
                analysis["points_to_homepage"] = True
                analysis["detected_type"] = "non_repository_url"

        has_pitfall = analysis["points_to_homepage"]
        return has_pitfall, analysis

    def analyze_codemeta_pitfalls(self, repo_path: Path) -> Dict:
        """Analyze codemeta.json pitfalls in a repository."""
        repo_name = repo_path.name
        result = {
            "repository": repo_name,
            "has_codemeta": False,
            "codemeta_file": None,
            "codemeta_location": None,
            "has_software_requirements_without_versions": False,
            "software_requirements_analysis": {},
            "has_readme_pointing_to_non_readme": False,
            "readme_analysis": {},
            "has_license_pointing_to_local_file": False,
            "license_analysis": {},
            "has_software_version_as_branch": False,
            "software_version_analysis": {},
            "has_software_requirements_with_local_file_urls": False,
            "software_requirements_local_files_analysis": {},
            "has_programming_languages_without_versions": False,
            "programming_languages_analysis": {},
            "has_software_requirements_with_homepage_urls": False,
            "software_requirements_homepage_analysis": {},
            "has_empty_identifier": False,
            "identifier_analysis": {},
            "has_keywords_as_string": False,
            "keywords_analysis": {},
            "has_code_repository_pointing_to_homepage": False,
            "code_repository_analysis": {}
        }

        codemeta_result = self._find_file_recursive(repo_path, self.codemeta_filenames)

        if not codemeta_result:
            return result

        codemeta_file, codemeta_location = codemeta_result
        result["has_codemeta"] = True
        result["codemeta_file"] = codemeta_file.name
        result["codemeta_location"] = codemeta_location.name

        try:
            codemeta_content = self._read_json_file(codemeta_file)

            print(f"DEBUG - Repository: {repo_name}")
            print(f"DEBUG - Reading file: {codemeta_file}")
            print(f"DEBUG - Read result keys: {list(codemeta_content.keys())}")

            if "error" in codemeta_content:
                result["codemeta_error"] = codemeta_content["error"]
                print(f"DEBUG - Error reading JSON: {codemeta_content['error']}")
                return result

            codemeta_data = codemeta_content["content"]
            print(f"DEBUG - Codemeta data type: {type(codemeta_data)}")
            print(
                f"DEBUG - Codemeta keys: {list(codemeta_data.keys()) if isinstance(codemeta_data, dict) else 'Not a dict'}")

            if isinstance(codemeta_data, dict):
                sw_req_key = None
                for key in codemeta_data.keys():
                    if key.lower() in ['softwarerequirements', 'software_requirements']:
                        sw_req_key = key
                        break
                print(f"DEBUG - Found softwareRequirements key: {sw_req_key}")
                if sw_req_key:
                    print(f"DEBUG - softwareRequirements value: {codemeta_data[sw_req_key]}")

            has_sw_req_pitfall, sw_req_analysis = self._analyze_software_requirements(codemeta_data)
            result["has_software_requirements_without_versions"] = has_sw_req_pitfall
            result["software_requirements_analysis"] = sw_req_analysis
            print(
                f"DEBUG - Software requirements analysis result: has_pitfall={has_sw_req_pitfall}, analysis={sw_req_analysis}")

            has_sw_req_local_pitfall, sw_req_local_analysis = self._analyze_software_requirements_local_files(
                codemeta_data)
            result["has_software_requirements_with_local_file_urls"] = has_sw_req_local_pitfall
            result["software_requirements_local_files_analysis"] = sw_req_local_analysis

            has_sw_req_homepage_pitfall, sw_req_homepage_analysis = self._analyze_software_requirements_homepage_urls(
                codemeta_data)
            result["has_software_requirements_with_homepage_urls"] = has_sw_req_homepage_pitfall
            result["software_requirements_homepage_analysis"] = sw_req_homepage_analysis

            has_req_local_pitfall, req_local_analysis = self._analyze_software_requirements_local_files(codemeta_data)
            result["has_software_requirements_with_local_file_urls"] = has_req_local_pitfall
            result["software_requirements_local_files_analysis"] = req_local_analysis

            has_req_homepage_pitfall, req_homepage_analysis = self._analyze_software_requirements_homepage_urls(
                codemeta_data)
            result["has_software_requirements_with_homepage_urls"] = has_req_homepage_pitfall
            result["software_requirements_homepage_analysis"] = req_homepage_analysis

            has_readme_pitfall, readme_analysis = self._analyze_readme_property(codemeta_data)
            result["has_readme_pointing_to_non_readme"] = has_readme_pitfall
            result["readme_analysis"] = readme_analysis

            has_license_pitfall, license_analysis = self._analyze_license_property(codemeta_data)
            result["has_license_pointing_to_local_file"] = has_license_pitfall
            result["license_analysis"] = license_analysis

            has_version_pitfall, version_analysis = self._analyze_software_version(codemeta_data)
            result["has_software_version_as_branch"] = has_version_pitfall
            result["software_version_analysis"] = version_analysis

            has_prog_lang_pitfall, prog_lang_analysis = self._analyze_programming_languages_versions(codemeta_data)
            result["has_programming_languages_without_versions"] = has_prog_lang_pitfall
            result["programming_languages_analysis"] = prog_lang_analysis

            has_identifier_pitfall, identifier_analysis = self._analyze_identifier_empty(codemeta_data)
            result["has_empty_identifier"] = has_identifier_pitfall
            result["identifier_analysis"] = identifier_analysis

            has_keywords_pitfall, keywords_analysis = self._analyze_keywords_string_instead_of_list(codemeta_data)
            result["has_keywords_as_string"] = has_keywords_pitfall
            result["keywords_analysis"] = keywords_analysis

            has_code_repo_pitfall, code_repo_analysis = self._analyze_code_repository_homepage_url(codemeta_data)
            result["has_code_repository_pointing_to_homepage"] = has_code_repo_pitfall
            result["code_repository_analysis"] = code_repo_analysis


        except Exception as e:

            result["codemeta_error"] = str(e)

            print(f"DEBUG - Exception in analyze_codemeta_pitfalls: {str(e)}")

            import traceback

            traceback.print_exc()

        return result

    def analyze_repository(self, repo_path: Path) -> Dict:
        """Analyze a single repository for all pitfalls."""
        license_analysis = self.analyze_license_pitfalls(repo_path)
        codemeta_analysis = self.analyze_codemeta_pitfalls(repo_path)

        combined_result = {
            "repository": repo_path.name,
            **license_analysis,
            **{k: v for k, v in codemeta_analysis.items() if k != "repository"}
        }

        return combined_result

    def analyze_all_repositories(self) -> Dict:
        """Analyze all repositories in the temp_analysis directory."""
        repositories = self._get_repositories()
        results = []

        license_stats = {
            "repositories_with_license": 0,
            "repositories_with_license_placeholders": 0,
            "repositories_with_license_copyright_only": 0
        }

        codemeta_stats = {
            "repositories_with_codemeta": 0,
            "repositories_with_software_requirements": 0,
            "repositories_with_software_requirements_without_versions": 0,
            "repositories_with_software_requirements_with_local_file_urls": 0,
            "repositories_with_software_requirements_with_homepage_urls": 0,
            "repositories_with_readme_property": 0,
            "repositories_with_readme_pointing_to_non_readme": 0,
            "repositories_with_license_property": 0,
            "repositories_with_license_pointing_to_local_file": 0,
            "repositories_with_software_version": 0,
            "repositories_with_software_version_as_branch": 0,
            "repositories_with_programming_languages": 0,
            "repositories_with_programming_languages_without_versions": 0,
            "repositories_with_identifier": 0,
            "repositories_with_empty_identifier": 0,
            "repositories_with_keywords": 0,
            "repositories_with_keywords_as_string": 0,
            "repositories_with_code_repository": 0,
            "repositories_with_code_repository_pointing_to_homepage": 0
        }

        print(f"Found {len(repositories)} repositories to analyze...")

        for repo_path in repositories:
            print(f"Analyzing repository: {repo_path.name}")
            result = self.analyze_repository(repo_path)
            results.append(result)

            if result["has_license"]:
                license_stats["repositories_with_license"] += 1

                if result["has_license_placeholders"]:
                    license_stats["repositories_with_license_placeholders"] += 1
                    print(f"  ⚠️  LICENSE placeholders: {result['license_placeholders_found']}")
                elif result["has_license_copyright_only"]:
                    license_stats["repositories_with_license_copyright_only"] += 1
                    content_type = result["license_copyright_analysis"].get("content_type", "unknown")
                    categories = result["license_copyright_analysis"].get("estimated_content_categories", [])
                    print(f"  ⚠️  LICENSE copyright-only ({content_type}): {categories}")
                else:
                    print(f"  ✅ LICENSE: No pitfalls found")
            else:
                print(f"  ❌ No LICENSE file found")

            if result["has_codemeta"]:
                codemeta_stats["repositories_with_codemeta"] += 1

                if result["software_requirements_analysis"].get("has_software_requirements", False):
                    codemeta_stats["repositories_with_software_requirements"] += 1
                    if result["has_software_requirements_without_versions"]:
                        codemeta_stats["repositories_with_software_requirements_without_versions"] += 1
                        missing_items = result["software_requirements_analysis"].get("missing_version_items", [])
                        structure_type = result["software_requirements_analysis"].get("structure_type", "unknown")
                        print(
                            f"  ⚠️  CODEMETA ({structure_type}): Software requirements without versions: {missing_items}")
                    else:
                        structure_type = result["software_requirements_analysis"].get("structure_type", "unknown")
                        print(f"  ✅ CODEMETA ({structure_type}): All software requirements have versions")
                else:
                    print(f"  ℹ️  CODEMETA: No software requirements found (not a pitfall)")

                if result["software_requirements_local_files_analysis"].get("has_software_requirements", False):
                    if result["has_software_requirements_with_local_file_urls"]:
                        codemeta_stats["repositories_with_software_requirements_with_local_file_urls"] += 1
                        local_file_items = result["software_requirements_local_files_analysis"].get(
                            "local_file_url_items", [])
                        structure_type = result["software_requirements_local_files_analysis"].get("structure_type",
                                                                                                  "unknown")
                        urls = [item["url"] for item in local_file_items]
                        print(f"  ⚠️  CODEMETA ({structure_type}): Software requirements point to local files: {urls}")
                    else:
                        structure_type = result["software_requirements_local_files_analysis"].get("structure_type",
                                                                                                  "unknown")
                        print(
                            f"  ✅ CODEMETA ({structure_type}): Software requirements properly specified (no local file URLs)")

                if result["software_requirements_homepage_analysis"].get("has_software_requirements", False):
                    if result["has_software_requirements_with_homepage_urls"]:
                        codemeta_stats["repositories_with_software_requirements_with_homepage_urls"] += 1
                        homepage_items = result["software_requirements_homepage_analysis"].get("homepage_url_items", [])
                        structure_type = result["software_requirements_homepage_analysis"].get("structure_type",
                                                                                               "unknown")
                        urls = [item["url"] for item in homepage_items]
                        print(f"  ⚠️  CODEMETA ({structure_type}): Software requirements point to homepages: {urls}")

                if result["programming_languages_analysis"].get("has_programming_languages", False):
                    codemeta_stats["repositories_with_programming_languages"] += 1
                    if result["has_programming_languages_without_versions"]:
                        codemeta_stats["repositories_with_programming_languages_without_versions"] += 1
                        missing_items = result["programming_languages_analysis"].get("missing_version_items", [])
                        structure_type = result["programming_languages_analysis"].get("structure_type", "unknown")
                        print(
                            f"  ⚠️  CODEMETA ({structure_type}): Programming languages without versions: {missing_items}")
                    else:
                        structure_type = result["programming_languages_analysis"].get("structure_type", "unknown")
                        print(f"  ✅ CODEMETA ({structure_type}): All programming languages have versions")

                if result["identifier_analysis"].get("has_identifier", False):
                    codemeta_stats["repositories_with_identifier"] += 1
                    if result["has_empty_identifier"]:
                        codemeta_stats["repositories_with_empty_identifier"] += 1
                        identifier_type = result["identifier_analysis"].get("identifier_type", "unknown")
                        print(f"  ⚠️  CODEMETA: Empty identifier ({identifier_type})")
                    else:
                        print(f"  ✅ CODEMETA: Identifier properly specified")

                if result["keywords_analysis"].get("has_keywords", False):
                    codemeta_stats["repositories_with_keywords"] += 1
                    if result["has_keywords_as_string"]:
                        codemeta_stats["repositories_with_keywords_as_string"] += 1
                        keywords_value = result["keywords_analysis"].get("keywords_value", "")
                        parsed_keywords = result["keywords_analysis"].get("parsed_keywords", [])
                        print(
                            f"  ⚠️  CODEMETA: Keywords as string instead of list: '{keywords_value}' -> {parsed_keywords}")
                    else:
                        print(f"  ✅ CODEMETA: Keywords properly specified as list")

                # Code repository analysis
                if result["code_repository_analysis"].get("has_code_repository", False):
                    codemeta_stats["repositories_with_code_repository"] += 1
                    if result["has_code_repository_pointing_to_homepage"]:
                        codemeta_stats["repositories_with_code_repository_pointing_to_homepage"] += 1
                        detected_type = result["code_repository_analysis"].get("detected_type", "unknown")
                        repo_url = result["code_repository_analysis"].get("code_repository_value", "")
                        print(f"  ⚠️  CODEMETA: Code repository points to {detected_type}: {repo_url}")
                    else:
                        print(f"  ✅ CODEMETA: Code repository properly specified")

            else:
                print(f"  ❌ No codemeta.json file found")

        prog_lang_percentage = (
            (codemeta_stats["repositories_with_programming_languages_without_versions"] /
             codemeta_stats["repositories_with_programming_languages"] * 100)
            if codemeta_stats["repositories_with_programming_languages"] > 0 else 0
        )

        identifier_percentage = (
            (codemeta_stats["repositories_with_empty_identifier"] /
             codemeta_stats["repositories_with_identifier"] * 100)
            if codemeta_stats["repositories_with_identifier"] > 0 else 0
        )

        keywords_percentage = (
            (codemeta_stats["repositories_with_keywords_as_string"] /
             codemeta_stats["repositories_with_keywords"] * 100)
            if codemeta_stats["repositories_with_keywords"] > 0 else 0
        )

        code_repo_percentage = (
            (codemeta_stats["repositories_with_code_repository_pointing_to_homepage"] /
             codemeta_stats["repositories_with_code_repository"] * 100)
            if codemeta_stats["repositories_with_code_repository"] > 0 else 0
        )

        homepage_req_percentage = (
            (codemeta_stats["repositories_with_software_requirements_with_homepage_urls"] /
             codemeta_stats["repositories_with_software_requirements"] * 100)
            if codemeta_stats["repositories_with_software_requirements"] > 0 else 0
        )

        license_percentage = (
            (license_stats["repositories_with_license_placeholders"] / license_stats["repositories_with_license"] * 100)
            if license_stats["repositories_with_license"] > 0 else 0
        )

        codemeta_req_percentage = (
            (codemeta_stats["repositories_with_software_requirements_without_versions"] /
             codemeta_stats["repositories_with_software_requirements"] * 100)
            if codemeta_stats["repositories_with_software_requirements"] > 0 else 0
        )

        codemeta_req_local_percentage = (
            (codemeta_stats["repositories_with_software_requirements_with_local_file_urls"] /
             codemeta_stats["repositories_with_software_requirements"] * 100)
            if codemeta_stats["repositories_with_software_requirements"] > 0 else 0
        )

        readme_percentage = (
            (codemeta_stats["repositories_with_readme_pointing_to_non_readme"] /
             codemeta_stats["repositories_with_readme_property"] * 100)
            if codemeta_stats["repositories_with_readme_property"] > 0 else 0
        )

        license_local_percentage = (
            (codemeta_stats["repositories_with_license_pointing_to_local_file"] /
             codemeta_stats["repositories_with_license_property"] * 100)
            if codemeta_stats["repositories_with_license_property"] > 0 else 0
        )

        license_placeholder_percentage = (
            (license_stats["repositories_with_license_placeholders"] /
             license_stats["repositories_with_license"] * 100)
            if license_stats["repositories_with_license"] > 0 else 0
        )

        license_copyright_only_percentage = (
            (license_stats["repositories_with_license_copyright_only"] /
             license_stats["repositories_with_license"] * 100)
            if license_stats["repositories_with_license"] > 0 else 0
        )

        version_branch_percentage = (
            (codemeta_stats["repositories_with_software_version_as_branch"] /
             codemeta_stats["repositories_with_software_version"] * 100)
            if codemeta_stats["repositories_with_software_version"] > 0 else 0
        )

        summary = {
            "total_repositories_found": len(repositories),
            "license_analysis": {
                **license_stats,
                "percentage_with_license_placeholders": round(license_placeholder_percentage, 2),
                "percentage_with_license_copyright_only": round(license_copyright_only_percentage, 2)
            },

            "codemeta_analysis": {
                **codemeta_stats,
                "percentage_with_software_requirements_without_versions": round(codemeta_req_percentage, 2),
                "percentage_with_software_requirements_with_local_file_urls": round(codemeta_req_local_percentage, 2),
                "percentage_with_software_requirements_with_homepage_urls": round(homepage_req_percentage, 2),
                "percentage_with_readme_pointing_to_non_readme": round(readme_percentage, 2),
                "percentage_with_license_pointing_to_local_file": round(license_local_percentage, 2),
                "percentage_with_software_version_as_branch": round(version_branch_percentage, 2),
                "percentage_with_programming_languages_without_versions": round(prog_lang_percentage, 2),
                "percentage_with_empty_identifier": round(identifier_percentage, 2),
                "percentage_with_keywords_as_string": round(keywords_percentage, 2),
                "percentage_with_code_repository_pointing_to_homepage": round(code_repo_percentage, 2)
            },
            "detailed_results": results
        }

        return summary

    def save_results_to_json(self, results: Dict, output_file: str = "pitfall_analysis_results.json"):

        output_path = Path(output_file)

        with open(output_path, 'w', encoding='utf-8') as file:
            json.dump(results, file, indent=2, ensure_ascii=False)

        print(f"Results saved to: {output_path.absolute()}")