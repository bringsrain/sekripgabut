from setuptools import setup, find_packages


setup(
    name="sekripgabut",
    version="0.5.0",
    py_modules=["main"],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    exclude_package_data={
        "": ["*.ini",
             "*.log",
             "notes.md",
             "*.BAK",
             "*.bak",
             "*.json",
             "testing_dir",
             "testing_dir/*"],
    },
    install_requires=[
        "requests>=2.32.3",
        "jmespath>=1.0.1",
    ],
    entry_points={
        "console_scripts": [
            "sekripgabut=sekripgabut.cli:main",
        ],
    },
    description=(
        "Koleksi skrip-skrip hasil gabut dadakan, yang mungkin saja useless"),
    author="Ari Selpama Diutri",
    author_email="ariselpamadiutri@gmail.com",
    url="https://github.com/bringsrain/sekripgabut",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)
