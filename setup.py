import os
from setuptools import setup, find_packages

setup(
    name='biggest',
    description='A utility for finding the biggest files and/or directories in a directory tree',
    url='https://github.com/ESultanik/biggest',
    author='Evan Sultanik',
    version='3.0.1',
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=[
        'colorama',
    ],
    entry_points={
        'console_scripts': [
            'biggest = biggest.__main__:main'
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Topic :: Utilities'
    ]
)
