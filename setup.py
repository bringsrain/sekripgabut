from setuptools import setup, find_packages


setup(
    name="sekripgabut",
    version="0.2.0",
    packages=find_packages(),
    include_package_data=True,
    exclude_package_data={
        "": ["fs.ini",],
    },
    install_requires=[
        "requests>=2.32.3",
    ],
    entry_points={
        "console_scripts": [
            "sekripgabut=sekripgabut:main",
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
    python_requires=">=3.12",
)
