# Flask-MongoEngine

[![PyPI version](https://badge.fury.io/py/flask-mongoengine.svg)](https://badge.fury.io/py/flask-mongoengine)
[![CI Tests](https://github.com/MongoEngine/flask-mongoengine/actions/workflows/tests.yml/badge.svg)](https://github.com/MongoEngine/flask-mongoengine/actions/workflows/tests.yml)
[![Documentation Status](https://readthedocs.org/projects/flask-mongoengine/badge/?version=latest)](http://docs.mongoengine.org/projects/flask-mongoengine/en/latest/?badge=latest)
[![Maintainability](https://api.codeclimate.com/v1/badges/6fb8ae00b1008f5f1b20/maintainability)](https://codeclimate.com/github/MongoEngine/flask-mongoengine/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/6fb8ae00b1008f5f1b20/test_coverage)](https://codeclimate.com/github/MongoEngine/flask-mongoengine/test_coverage)
![PyPI - Downloads](https://img.shields.io/pypi/dm/flask-mongoengine)

Flask-MongoEngine is a Flask extension that provides integration with [MongoEngine]
and [FlaskDebugToolbar].

## Installation

By default, Flask-MongoEngine will install integration only between [Flask] and
[MongoEngine]. Integration with [FlaskDebugToolbar] are optional and
should be selected as extra option, if required. This is done by users request, to
limit amount of external dependencies in different production setup environments.

All methods end extras described below are compatible between each other and can be
used together.

### Installation with MongoEngine only support

```bash
# For Flask >= 2.3.0
pip install flask-mongoengine
```

### Installation with Flask Debug Toolbar support

Flask-mongoengine provide beautiful extension to [FlaskDebugToolbar] allowing to monitor
all database requests. To use this extension [FlaskDebugToolbar] itself required. If
you need to install flask-mongoengine with related support, use:

```bash
# With FlaskDebugToolbar dependencies
pip install flask-mongoengine[toolbar]
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

Flask-MongoEngine is distributed under [BSD 3-Clause License].

[MongoEngine]: https://github.com/MongoEngine/mongoengine

[FlaskDebugToolbar]: https://github.com/flask-debugtoolbar/flask-debugtoolbar

[read the docs]: http://docs.mongoengine.org/projects/flask-mongoengine/

[Flask]: https://github.com/pallets/flask

[BSD 3-Clause License]: LICENSE.md

[Contribution guidelines]: CONTRIBUTING.md

[complete connection settings description]: http://docs.mongoengine.org/projects/flask-mongoengine/flask_config.html
