=================
Flask-MongoEngine
=================
:Info: MongoEngine for Flask web applications.
:Repository: https://github.com/MongoEngine/flask-mongoengine

.. image:: https://travis-ci.org/MongoEngine/flask-mongoengine.svg?branch=master
  :target: https://travis-ci.org/MongoEngine/flask-mongoengine

About
=====
Flask-MongoEngine is a Flask extension that provides integration with MongoEngine. It handles connection management for your app.
You can also use WTForms as model forms for your models.

Documentation
=============
You can find the documentation at https://flask-mongoengine.readthedocs.io

Installation
============
You can install this package using pypi: ``pip install flask-mongoengine``

Tests
=====
To run the test suite, ensure you are running a local copy of Flask-MongoEngine
and run: ``python setup.py nosetests``.

To run the test suite on every supported versions of Python, PyPy and MongoEngine you can use ``tox``.
Ensure tox and each supported Python, PyPy versions are installed in your environment:

.. code-block:: shell

    # Install tox
    $ pip install tox
    # Run the test suites
    $ tox

To run a single or selected test suits, use the nosetest convention. E.g.

.. code-block:: shell

    $ python setup.py nosetests --tests tests/example_test.py:ExampleTestClass.example_test_method

Contributing
============
We welcome contributions! see  the `Contribution guidelines <https://github.com/MongoEngine/flask-mongoengine/blob/master/CONTRIBUTING.rst>`_

Community
=========
- `#flask-mongoengine IRC channel <http://webchat.freenode.net/?channels=flask-mongoengine>`_

License
=======
Flask-MongoEngine is distributed under MIT license, see LICENSE for more details.
