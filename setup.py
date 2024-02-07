from setuptools import setup, find_packages
from pathlib import Path


curr_ = Path(__file__).parent
long_description = (curr_ / 'README.md').read_text()

setup(
    name='dcl2nwb',
    version='0.1.0',
    author='Hamidreza Alimohammadi',
    author_email="<alimohammadi.hamidreza@gmail.com>",
    description='adaptive and customizable conversion tool to standardize the data storage of '
                'Defense Circuits Lab (DCL) into NWB format',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    keywords=['Python', 'NWB', 'ReTune', 'DCL'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Linux :: Ubuntu",
        "Operating System :: Microsoft :: Windows",
    ]
)
