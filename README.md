# Flask-MongoEngine2

[![PyPI version](https://badge.fury.io/py/flask-mongoengine2.svg)](https://badge.fury.io/py/flask-mongoengine2)
[![CI Tests](https://github.com/ahmetelgun/flask-mongoengine2/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/ahmetelgun/flask-mongoengine2/actions/workflows/tests.yml)
[![Documentation Status](https://readthedocs.org/projects/flask-mongoengine2/badge/?version=latest)](http://docs.mongoengine.org/projects/flask-mongoengine2/en/latest/?badge=latest)
[![Maintainability](https://api.codeclimate.com/v1/badges/709e5854f7b76b27637c/maintainability)](https://codeclimate.com/github/ahmetelgun/flask-mongoengine2/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/709e5854f7b76b27637c/test_coverage)](https://codeclimate.com/github/ahmetelgun/flask-mongoengine2/test_coverage)
![PyPI - Downloads](https://img.shields.io/pypi/dm/flask-mongoengine2)

Flask-MongoEngine2 is a Flask extension that provides integration with [MongoEngine]
and [FlaskDebugToolbar].

## Installation

By default, Flask-MongoEngine2 will install integration only between [Flask] and
[MongoEngine]. Integration with [FlaskDebugToolbar] are optional and
should be selected as extra option, if required. This is done by users request, to
limit amount of external dependencies in different production setup environments.

All methods end extras described below are compatible between each other and can be
used together.

### Installation with MongoEngine only support

```bash
# For Flask >= 2.3.0
pip install flask-mongoengine2
```

### Installation with Flask Debug Toolbar support

Flask-mongoengine provide beautiful extension to [FlaskDebugToolbar] allowing to monitor
all database requests. To use this extension [FlaskDebugToolbar] itself required. If
you need to install flask-mongoengine2 with related support, use:

```bash
# With FlaskDebugToolbar dependencies
pip install flask-mongoengine2[toolbar]
```

## Flask configuration

Flask-mongoengine does not provide any configuration defaults. User is responsible
for setting up correct database settings, to exclude any possible misconfiguration
and data corruption.

There are several options to set connection. Please note, that all except
recommended are deprecated and may be removed in future versions, to lower code base
complexity and bugs. If you use any deprecated connection settings approach, you should
update your application configuration.

Please refer to [complete connection settings description] for more info.

## Usage and API documentation

Full project documentation available on [read the docs].

## Contributing and testing

We are welcome for contributors and testers! Check [Contribution guidelines].

## License

Flask-MongoEngine2 is distributed under [BSD 3-Clause License].

[MongoEngine]: https://github.com/MongoEngine/mongoengine

[FlaskDebugToolbar]: https://github.com/flask-debugtoolbar/flask-debugtoolbar

[read the docs]: https://flask-mongoengine2.readthedocs.io/en/latest/

[Flask]: https://github.com/pallets/flask

[BSD 3-Clause License]: LICENSE.md

[Contribution guidelines]: CONTRIBUTING.md
