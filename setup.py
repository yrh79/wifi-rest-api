# -*- encoding: utf-8 -*-

from glob import glob
import os
from os.path import basename
from os.path import splitext

from setuptools import find_packages
from setuptools import setup


def load_requirements():
    fname = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    with open(fname, "rt") as f:
        data = f.read()
        if not data:
            return []
        return data.splitlines()


setup(
    name='wifi-rest',
    version='0.0.1',
    description='Registration api for the wifiSwitchControl project',
    long_description='',
    author='',
    author_email='',
    url='',
    packages=find_packages('src'),
    package_dir={'': './src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src.*.py')],
    include_package_data=True,
    package_data={
    },
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Platform',
    ],
    install_requires=load_requirements(),
    extras_require={
        'dev': [
            'pytest',
            'pytest-pep8',
            'pytest-cov',
        ]
    }
)
