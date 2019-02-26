from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

setup(
    name='ez-json-traverse', 
    version='0.2',
    packages=find_packages(),
    author='buhanec',
    license='MIT',
    description='Easier traversing and exploration of JSON structures',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/buhanec/ez-json-traverse',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)
