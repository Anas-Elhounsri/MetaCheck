from setuptools import setup, find_namespace_packages

setup(
    name="metacheck",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_namespace_packages(where="src"),
    install_requires=[
        "requests",
        "somef",
    ],
    entry_points={
        "console_scripts": [
            "detect-pitfalls=metacheck.cli:cli",
        ],
    },
    author="Anas El Hounsri",
    description="Detect metadata pitfalls in software repositories",
)
