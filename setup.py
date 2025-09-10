import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as f:
    install_requires = f.read().splitlines()

setuptools.setup(
    name="socketio-proxy",
    version="0.1.0",
    author="v4ner",
    author_email="v4ner@proton.me",
    description="A proxy for socket.io events.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/v4ner/socketio_proxy",
    packages=setuptools.find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=install_requires,
)