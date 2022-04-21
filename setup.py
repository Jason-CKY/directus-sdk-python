from setuptools import setup, find_packages
from directus import __version__

setup(
    name='directus-sdk',
    version=__version__,
    description='python SDK for directus client wiht convenience functions',
    url='https://github.com/Jason-CKY/directus-sdk-python',
    author='Jason Cheng',
    packages=find_packages(exclude=['examples']),
    install_requires=['requests']
)