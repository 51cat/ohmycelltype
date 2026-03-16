from setuptools import setup, find_packages

setup(
    name="ohmycelltype",
    version="0.1.0",
    description="A comprehensive workflow for single-cell RNA-seq cell type annotation using LLMs",
    author="zhliu",
    author_email="lzh1996035@163.com",
    packages=find_packages(),
    install_requires=[
        "openai",
        "pandas",
        "requests",
        "rich>=13.0.0",
        "click>=8.0.0",
        "markdown>=3.0.0"
    ],
    entry_points={
        'console_scripts': [
            'ohmycelltype=ohmycelltype.cli:main',
        ],
    },
)