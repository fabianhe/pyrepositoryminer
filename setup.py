from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pyrepositoryminer",
    version="0.0.1",
    author="Fabian Heseding",
    author_email="39628987+fabianhe@users.noreply.github.com",
    description="Efficient Repository Mining in Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/fabianhe/pyrepositoryminer",
    project_urls={
        "Bug Tracker": "https://github.com/fabianhe/pyrepositoryminer/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
)
