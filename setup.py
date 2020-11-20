import os
from setuptools import setup


description = (
    "Flask-MongoEngine is a Flask extension "
    "that provides integration with MongoEngine and WTF model forms."
)

# Load index.rst as long_description
doc_path = os.path.join(os.path.dirname(__file__), "docs", "index.rst")
long_description = open(doc_path, encoding="utf-8").read()
long_description_content_type = "text/x-rst"

# Stops exit traceback on tests
try:
    import multiprocessing  # noqa
except ImportError:
    pass


def get_version(version_tuple):
    """Return the version tuple as a string, e.g. for (0, 10, 7),
    return '0.10.7'.
    """
    return ".".join(map(str, version_tuple))


# Dirty hack to get version number from flask_monogengine/__init__.py - we
# can't import it as it depends on PyMongo and PyMongo isn't installed until
# this file is read
init = os.path.join(os.path.dirname(__file__), "flask_mongoengine", "__init__.py")
version_line = list(filter(lambda l: l.startswith("VERSION"), open(init)))[0]
version = get_version(eval(version_line.split("=")[-1]))

test_requirements = ["coverage", "pytest", "pytest-cov"]

setup(
    name="flask-mongoengine",
    version=version,
    url="https://github.com/mongoengine/flask-mongoengine",
    license="BSD",
    author="Ross Lawley",
    author_email="ross.lawley@gmail.com",
    zip_safe=False,
    platforms="any",
    install_requires=[
        "Flask>=1.1.2",
        "WTForms[email]>=2.3.1",
        "Flask-WTF>=0.14.3",
        "mongoengine>=0.20",
    ],
    packages=["flask_mongoengine", "flask_mongoengine.wtf"],
    include_package_data=True,
    tests_require=test_requirements,
    description=description,
    long_description=long_description,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Framework :: Flask",
    ],
)
