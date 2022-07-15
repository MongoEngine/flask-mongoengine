# Contributing guide

MongoEngine has a large [community] and contributions are always encouraged.
Contributions can be as simple as typo fix in the documentation, as well as complete
new features and integrations. Please read these guidelines before sending a pull
request.

## Bugfixes and new features

Before starting to write code, look for existing [tickets] or create one for your
specific issue or feature request. That way you avoid working on something
that might not be of interest or that has already been addressed.

For new integrations do you best to make integration optional, to leave user
opportunity to exclude additional dependencies, in case when user do not need
integration or feature.

## Supported interpreters

Flask-MongoEngine supports CPython 3.7 and newer, PyPy 3.7 and newer. Language features
not supported by all interpreters can not be used.

## Running tests

All development requirements, except [docker] are included in package extra options
`dev`. So, to install full development environment you need just run package with
all related options installation.

Our local test environment related on [docker] and [nox] to test project on real
database engine and not use any database mocking, as such mocking can raise unexpected
behaviour, that is not seen in real database engines.

Before running tests, please ensure that real database not launched on local port
``27017``, otherwise tests will fail. If you want to run tests with local launched
database engine, run tests in non-interactive mode (see below), in this case [docker]
will not be used at all.

We do not include docker python package to requirements, to exclude harming local
developer's system, if docker installed in recommended/other way.

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

## Setting up the code for local development and tests

1. Fork the `flask-mongoengine` repo on GitHub.
2. Clone your fork locally:

   ```bash
   git clone git@github.com:your_name_here/flask-mongoengine.git
   ```

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper
   installed, this is how you set up your fork for local development with all
   required development and testing dependencies (except docker):

   ```bash
   cd flask-mongoengine/
   # With all development and package requirements, except docker
   pip install -e .[wtf,toolbar,dev]
   ```

4. Create a branch for local development:

   ```bash
   git checkout -b name-of-your-bugfix-or-feature
   ```

   Now you can make your changes locally.
5. When you're done making changes, check that your changes pass the tests and lint
   check:

   ```bash
   nox
   ```

   Please note that [nox] runs lint and documentation builds check automatically,
   since we have a test environment for it. During lint check run, some common
   issues will be fixed automatically, so in case of failed status, firstly just try
   to rerun check again. If issue is not fixed automatically, check run log.

   If you feel like running only the lint environment, please use the following command:

   ```bash
   nox -s lint
   ```

6. Ensure that your feature or commit is fully covered by tests. Check report after
   regular nox run.
7. Please install [pre-commit] git hook before adding any commits. This will
   ensure/fix 95% of linting issues. Otherwise, GitHub CI/CD pipeline may fail. This
   is linting double check (same as in [nox]), but it will run always, even if you
   forget to run tests before commit.

   ```bash
   pre-commit install
   ```

8. Commit your changes and push your branch to GitHub:

   ```bash
   git add .
   git commit -m "Your detailed description of your changes."
   git push origin name-of-your-bugfix-or-feature
   ```

9. Submit a pull request through the GitHub website.

## Interactive documentation development

Our nox configuration include special session for simplifying documentation
development. When launched, documentation will be re-rendered after any saved
code/documentation files changes. To use this session, after local environment setup,
just run:

```bash
nox -s docs
```

Rendered documentation will be available under: <http://localhost:9812/>

## Style guide

### General guidelines

- Avoid backward breaking changes if at all possible.
- Avoid mocking of external libraries; Mocking allowed only in tests.
- Avoid complex structures, for complex classes/methods/functions try to separate to
  little objects, to simplify code reuse and testing.
- Avoid code duplications, try to exctract duplicate code to function. (Code
  duplication in tests is allowed.)
- Write docstrings for new classes and methods.
- Write tests and make sure they pass.
- Add yourself to [AUTHORS.md] :)

### Code style guide

- Docstrings are using RST format. Developer encouraged to include any signigicant
  information to docstrings.
- Developers are encouraged to include typing information in functions signatures.
- Developers should avoid including typing information to docstrings, if possible.
- Developers should avoid including typing information to docstrings and signatures
  in same objects, to avoid rendering conflicts.
- Code formatting is completely done by [black] and following black's style
  implementation of [PEP8]. Target python version is the lowest supported version.
- Code formatting should be done before passing any new merge requests.
- Code style should use f-strings if possible, exceptional can be made for expensive
  debug level logging statements.

### Documentation style guide

- [Documentation] should use Markdown as main format. Including Rest syntax blocks
  inside are allowed. Exceptional is API auto modules documents. Our [documentation]
  engine support [MyST] markdown extensions.
- [Documentation] should use same 88 string length requirement, as code. Strings can
  be larger for cases, when last word/statement is any kind of link (either to
  class/function/attribute or web link).
- Weblinks should be placed at the end of document, to make [documentation] easy
  readable without rendering (in editor).
- Docs formatting should be checked and formatted with [pre-commit] plugin before
  submitting.

## CI/CD testing

All tests are run on [GitHub actions] and any pull requests are automatically tested
for full range of supported [Flask], [mongoengine], [python] and [mongodb] versions.
Any pull requests without tests will take longer to be integrated and might be refused.

[community]: AUTHORS.md

[tickets]: https://github.com/MongoEngine/flask-mongoengine/issues?state=open

[PEP8]: http://www.python.org/dev/peps/pep-0008/

[black]: https://github.com/psf/black

[pre-commit]: https://pre-commit.com/

[GitHub actions]: https://github.com/MongoEngine/flask-mongoengine/actions

[Flask]: https://github.com/pallets/flask

[mongoengine]: https://github.com/MongoEngine/mongoengine

[python]: https://www.python.org/

[mongodb]: https://www.mongodb.com/

[AUTHORS.md]: AUTHORS.md

[documentation]: http://docs.mongoengine.org/projects/flask-mongoengine/

[nox]: https://nox.thea.codes/en/stable/usage.html

[docker]: https://www.docker.com/

[MyST]: https://myst-parser.readthedocs.io/en/latest/syntax/syntax.html
