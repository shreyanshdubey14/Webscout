from setuptools import setup, find_packages

with open("README.md", encoding="utf-8") as f:
    README = f.read()

setup(
    name="webscout",
    version="2.3-beta",
    description="Search for anything using Google, DuckDuckGo, phind.com. Also contains AI models, can transcribe yt videos, temporary email and phone number generation, has TTS support, and webai (terminal gpt and open interpreter).",
    long_description=README,
    long_description_content_type="text/markdown",
    author="OEvortex",
    author_email="helpingai5@gmail.com",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=[
        "docstring_inheritance",
        "click",
        "curl_cffi",
        "lxml",
        "nest-asyncio",
        "selenium",
        "tqdm",
        "webdriver-manager",
        "halo>=0.0.31",
        "g4f>=0.2.2.3",
        "rich",
        "python-dotenv",
        "beautifulsoup4",
        "markdownify",
        "pydantic",
        "requests",
        "sse_starlette",
        "termcolor",
        "tiktoken",
        "tldextract",
        "orjson",
        "PyYAML",
        "appdirs",
        "GoogleBard1>=2.1.4",
        "tls_client",
        "clipman",
        "playsound",
    ],
    entry_points={
        "console_scripts": [
            "WEBS = webscout.cli:cli",
            "webscout = webscout.webai:main",
        ],
    },
    extras_require={
        "dev": [
            "ruff>=0.1.6",
            "pytest>=7.4.2",
        ],
        "local": [
            'llama-cpp-python',
            'colorama',
            'numpy',
        ],
    },
    license="HelpingAI Simplified Universal License",
    project_urls={
        "Documentation": "https://github.com/OE-LUCIFER/Webscout/wiki",
        "Source": "https://github.com/OE-LUCIFER/Webscout",
        "Tracker": "https://github.com/OE-LUCIFER/Webscout/issues",
        "YouTube": "https://youtube.com/@OEvortex",
    },
)