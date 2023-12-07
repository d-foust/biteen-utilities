import setuptools


with open("readme.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name='biteen_utilities',
    version='0.0.1',
    author='Daniel Foust',
    author_email='djfoust@umich.edu',
    description='Tools for working with single-molecule localization data.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    )
)