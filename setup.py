#!/usr/bin/env python

from setuptools import setup

setup(
    name='linkedin',
    version='0.1.2',
    install_requires=['httplib2', 'oauth2', 'simplejson'],
    author='Mike Helmick',
    author_email='mikehelmick@me.com',
    license='MIT License',
    url='https://github.com/michaelhelmick/linkedin/',
    keywords='python linkedin json oauth api',
    description='A Python Library to interface with LinkedIn API, OAuth and JSON responses',
    long_description=open('README.md').read(),
    download_url="https://github.com/michaelhelmick/linkedin/zipball/master",
    py_modules=["linkedin"],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet'
    ]
)
