# Flask-MongoEngine

[![PyPI version](https://badge.fury.io/py/flask-mongoengine.svg)](https://badge.fury.io/py/flask-mongoengine)
[![CI Tests](https://github.com/MongoEngine/flask-mongoengine/actions/workflows/tests.yml/badge.svg)](https://github.com/MongoEngine/flask-mongoengine/actions/workflows/tests.yml)
[![Documentation Status](https://readthedocs.org/projects/flask-mongoengine/badge/?version=latest)](http://docs.mongoengine.org/projects/flask-mongoengine/en/latest/?badge=latest)
[![Maintainability](https://api.codeclimate.com/v1/badges/6fb8ae00b1008f5f1b20/maintainability)](https://codeclimate.com/github/MongoEngine/flask-mongoengine/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/6fb8ae00b1008f5f1b20/test_coverage)](https://codeclimate.com/github/MongoEngine/flask-mongoengine/test_coverage)
![PyPI - Downloads](https://img.shields.io/pypi/dm/flask-mongoengine)

Flask-MongoEngine is a Flask extension that provides integration with [MongoEngine],
[WtfForms] and [FlaskDebugToolbar].

## Documentation

Full project documentation available on [read the docs].

## Installation

By default, Flask-MongoEngine will install integration only between [Flask] and
[MongoEngine]. Integration with [WTFForms] and [FlaskDebugToolbar] are optional and
should be selected as extra option, if required. This is done by users request, to
limit amount of external dependencies in different production setup environments.

Project packaging is done with setuptools, installation is expected by ``pip`` usage.

All methods end extras described below are compatible between each other and can be
used together.

### Installation with [MongoEngine] only support

```bash
# For Flask >= 2.0.0
pip install flask-mongoengine
```

We still maintain special case for [Flask] = 1.1.4 support (the latest version in 1.x.x
branch). To install flask-mongoengine with required dependencies use ``legacy``
extra option.

```bash
# With Flask 1.1.4 dependencies
pip install flask-mongoengine[legacy]
```

### Installation with WTF Forms support

Flask-mongoengine can be installed with [Flask-WTF] and [WTFForms] support. This
will extend project dependencies with [Flask-WTF], [WTFForms] and related packages.

```bash
# With Flask-WTF and WTFForms dependencies
pip install flask-mongoengine[wtf]
```

### Installation with Flask Debug Toolbar support

Flask-mongoengine provide beautiful extension to [FlaskDebugToolbar] allowing to monitor
all database requests. To use this extension [FlaskDebugToolbar] itself required. If
you need to install flask-mongoengine with related support, use:

```bash
# With FlaskDebugToolbar dependencies
pip install flask-mongoengine[toolbar]
```

## Development and tests

All development requirements, except [docker] are included in package extra options
``dev``. So, to install full development environment you need just run package with
all related options installation:

```bash
# With all development and package requirements, except docker
pip install flask-mongoengine[wtf,toolbar,dev]
```

Our test environment related on [docker] and [nox] to test project on real database
engine and not use any database mocking, as such mocking can raise unexpected
behaviour, that is not seen in real database engines.

Before running tests, please ensure that real database not launched on port
``27017``, otherwise tests will fail. If you want to run tests with local launched
database engine, run tests in non-interactive mode (see below), in this case [docker]
will not be used at all.

To run minimum amount of required tests with [docker], use:

```bash
nox
```

To run minimum amount of required tests with local database, use:

```bash
nox --non-interactive
```

To run one or mode nox sessions only, use `-s` option. For example to run only
documentation and linting tests, run:

```bash
nox -s documentation_tests lint
```

In some cases you will want to bypass arguments to pytest itself, to run single test
or single test file. It is easy to do, everything after double dash will be bypassed
to pytest directly. For example, to run ``test__normal_command__logged`` test only, use:

```bash
nox -- -k test__normal_command__logged
```

## Contributing

We are welcome for contributions! See the [Contribution guidelines].

## License

Flask-MongoEngine is distributed under [BSD 3-Clause License].

[MongoEngine]: https://github.com/MongoEngine/mongoengine

[WTFForms]: https://github.com/wtforms/wtforms

[Flask-WTF]: https://github.com/wtforms/flask-wtf

[FlaskDebugToolbar]: https://github.com/flask-debugtoolbar/flask-debugtoolbar

[read the docs]: http://docs.mongoengine.org/projects/flask-mongoengine/

[Flask]: https://github.com/pallets/flask

[BSD 3-Clause License]: LICENSE.md

[Contribution guidelines]: CONTRIBUTING.rst

[docker]: https://www.docker.com/

[nox]: https://nox.thea.codes/en/stable/usage.html
