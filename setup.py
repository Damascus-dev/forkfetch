from setuptools import setup


setup(
    name="fetcher",
    version="0.1.0",
    description="Smart GitHub repository discovery CLI",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Fetcher Maintainers",
    license="Proprietary",
    packages=["fetcher"],
    install_requires=[
        "httpx>=0.27.0,<1.0.0",
        "rich>=13.7.0,<14.0.0",
        "typer>=0.12.0,<1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "ffetch=fetcher.main:app",
        ]
    },
)
