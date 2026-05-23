from setuptools import setup, find_packages

setup(
    name="hiddenbytes",
    version="1.0.0",
    description="Binary Evasion & Polymorphic Toolkit (Educational)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="HiddenBytes",
    python_requires=">=3.8",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "hiddenbytes=hiddenbytes.__main__:main",
        ],
    },
    extras_require={
        "standalone": ["pyinstaller>=6.0"],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
    ],
)
