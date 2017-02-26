# -*= coding: utf-8 -*-

from setuptools import setup

setup(
    name="pyzaif",
    packages=['pyzaif'],
    version="0.1.1",
    description="Python wrapper for zaif's REST API",
    author="maki",
    author_email="makino.aaa@gmail.com",
    url="https://github.com/makino18/pyzaif",
    install_requires=['requests'],
    keywords=['bitcoin', 'zaif'],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    test_suite='test',
)