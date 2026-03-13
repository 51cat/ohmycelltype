from setuptools import setup, find_packages

setup(
    name="ohmycelltype",
    packages=find_packages(),
    install_requires=[
        "openai",
        "pandas",
        "requests",
        "rich>=13.0.0",
        "click>=8.0.0"
    ],
    entry_points={
        'console_scripts': [
            'ohmycelltype=ohmycelltype.cli:main',
        ],
    },
)