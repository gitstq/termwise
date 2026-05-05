from setuptools import setup, find_packages

setup(
    name="termwise",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.9",
    entry_points={
        "console_scripts": [
            "termwise=termwise.cli:main",
        ],
    },
)
