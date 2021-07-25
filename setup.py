#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='shorthand',
    version='0.1',
    description='Note Management utilities',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['shorthand-cli=shorthand.cli:run'],
    }
)
