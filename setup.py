from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gtool_registry_version",
    version="1.0.0",
    author="gtools team",
    author_email="team@gtools.dev",
    description="基于注册机制的功能调用和配置系统",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourorg/gtool_registry_version",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "gtools=gtools.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "gtools": ["*.py"],
    },
)