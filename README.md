# wifi-rest-api

This repository contains remote calling RESTful API of wifi switch server.

## Requirements
---------------

* redis
* Flask

See requirements.txt for complete list of requirements.

## Build
--------
Build Python package:

```shell
python setup.py bdist_wheel
```
The package built should locate at './dist/'.


## Installation
---------------

To install the package, first clone the repository:

```shell
git clone https://github.com/yrh79/wifi-rest-api.git
```

Next, from the root of the repository, install the package:
```shell
pip install .
```

Or, you can install a prebuild package:
```shell
pip install  path/to/wifi-rest-api-0.0.1-py3-none-any.whl
```

## Usage
---------------

Coming soon.

## Development
---------------

Developing the package requires:
* pytest
* pytest-pep8
* pytest-cov

In order to run tests, first the package must be installed into a virtual
environment with the development requirements:

    $ pip install .[dev]

To run tests, run the following command:

    $ pytest --cov --pep8
