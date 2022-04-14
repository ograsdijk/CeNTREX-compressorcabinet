import setuptools
from pathlib import Path

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

path = Path(__file__).parent / "centrex_compressorcabinet" / "dash" / "assets"

setuptools.setup(
    name="CeNTREX Compressor Cabinet",
    version="0.1",
    author="o.grasdijk",
    author_email="o.grasdijk@gmail.com",
    description="Python Dash GUI for the devices in the CeNTREX compressor cabinet.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=[
        "dash",
        "dash_bootstrap_components",
        "plotly",
        "pyzmq",
        "fastapi",
        "uvicorn",
    ],
    data_files=[
        ("centrex_compressorcabinet/dash/assets", [str(p) for p in path.iterdir()])
    ],
    classifiers=["Programming Language :: Python :: 3", "Operating System :: Windows"],
    python_requires=">=3.8",
)
