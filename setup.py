#!/usr/bin/env python

from setuptools import setup

setup(name='htmlmuncher',
    version='1.0',
    description='Utility that rewrites CSS, HTML, and JavaScript files in order to save bytes and obfuscate your code.',
    author='Craig Campbell',
    author_email='iamcraigcampbell@gmail.com',
    url='http://htmlmuncher.com',
    packages=['muncher'],
    scripts=['munch']
)
