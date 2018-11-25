import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pythonCommon",
    author="Alexander Maisch",
    description="SKilL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        #"License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
