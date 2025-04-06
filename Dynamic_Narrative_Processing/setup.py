from setuptools import setup, find_packages

setup(
    name="dynamic_narrative_processing",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "numpy>=1.21.0",
        "sentence-transformers>=2.2.2",
        "networkx>=2.6.3",
        "matplotlib>=3.4.3",
        "argparse>=1.4.0",
    ],
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="Dynamic Narrative Processing System for FSM-LLM Narrative",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
) 