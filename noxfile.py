"""Nox tool configuration file.

Nox is Tox tool replacement.
"""
import shutil
from pathlib import Path

import nox

nox.options.sessions = "latest", "lint", "documentation_tests"
db_version = "5.0"


def base_install(session, flask, mongoengine, toolbar):
    """Create basic environment setup for tests and linting."""
    session.run("python", "-m", "pip", "install", "--upgrade", "pip")
    session.run("python", "-m", "pip", "install", "setuptools_scm[toml]>=6.3.1")

    if toolbar:
        extra = "toolbar,"
    else:
        extra = ""

    session.install(
        f"Flask{flask}",
        f"mongoengine{mongoengine}",
        "-e",
        f".[{extra}dev]",
    )
    return session


@nox.session(python="3.12")
def lint(session):
    """Run linting check locally."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "-a")


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
@nox.parametrize("flask", [">=2.3.0", ">=3.0.0"])
@nox.parametrize(
    "mongoengine", ["==0.21.0", "==0.22.1", "==0.23.1", ">=0.24.1", ">=0.27.0"]
)
@nox.parametrize("toolbar", [True, False])
def ci_cd_tests(session, flask, mongoengine, toolbar):
    """Run test suite with pytest into ci_cd (no docker)."""
    session = base_install(session, flask, mongoengine, toolbar)
    session.run("pytest", *session.posargs)


def _run_in_docker(session):
    session.run(
        "docker",
        "run",
        "--name",
        "nox_docker_test",
        "-p",
        "27017:27017",
        "-d",
        f"mongo:{db_version}",
        external=True,
    )
    try:
        session.run("pytest", *session.posargs)
    finally:
        session.run_always("docker", "rm", "-fv", "nox_docker_test", external=True)


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
@nox.parametrize("flask", [">=2.3.0", ">=3.0.0"])
@nox.parametrize(
    "mongoengine", ["==0.21.0", "==0.22.1", "==0.23.1", ">=0.24.1", ">=0.27.0"]
)
@nox.parametrize("toolbar", [True, False])
def full_tests(session, flask, mongoengine, toolbar):
    """Run tests locally with docker and complete support matrix."""
    session = base_install(session, flask, mongoengine, toolbar)
    _run_in_docker(session)


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
@nox.parametrize("toolbar", [True, False])
def latest(session, toolbar):
    """Run minimum tests for checking minimum code quality."""
    flask = ">=3.0.0"
    mongoengine = ">=0.27.0"
    session = base_install(session, flask, mongoengine, toolbar)
    if session.interactive:
        _run_in_docker(session)
    else:
        session.run("pytest", *session.posargs)


@nox.session(python="3.10")
def documentation_tests(session):
    """Run documentation tests."""
    return docs(session, batch_run=True)


@nox.session(python="3.10")
def docs(session, batch_run: bool = False):
    """Build the documentation or serve documentation interactively."""
    shutil.rmtree(Path("docs").joinpath("_build"), ignore_errors=True)
    session.install("-r", "docs/requirements.txt")
    session.install("-e", ".[toolbar]")
    session.cd("docs")
    sphinx_args = ["-b", "html", "-W", ".", "_build/html"]

    if not session.interactive or batch_run:
        sphinx_cmd = "sphinx-build"
    else:
        sphinx_cmd = "sphinx-autobuild"
        sphinx_args.extend(
            [
                "--open-browser",
                "--port",
                "9812",
                "--watch",
                "../*.md",
                "--watch",
                "../*.rst",
                "--watch",
                "../*.py",
                "--watch",
                "../flask_mongoengine",
            ]
        )

    session.run(sphinx_cmd, *sphinx_args)
