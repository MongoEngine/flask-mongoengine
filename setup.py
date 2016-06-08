import os, imp
from setuptools import setup

def load_module(module_name, script_file):
    '''
    XXX: Load modules dynamically without
    triggering flask_mongoengine.__init__

    This way we do not encounter errors which
    requires dependencies to be pre-installed.
    '''
    module = None
    try:
        module = imp.load_source(module_name, script_file)
    except:
        pass
    return module

# Load MetaData
metadata_script = os.path.join(os.path.dirname(__file__), "flask_mongoengine", "metadata.py")
metadata = load_module("metadata", metadata_script)

# Load documentation
doc_path = os.path.join(os.path.dirname(__file__), "docs", "index.rst")

# Load guide
doc_path = os.path.join(os.path.dirname(__file__), "docs", "index.rst")
DESCRIPTION = 'Flask-MongoEngine is a Flask extension ' + \
'that provides integration with MongoEngine and WTF model forms.'

LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open(doc_path).read()

    # Stops exit traceback on tests
    import multiprocessing
except:
    pass

test_requirements = ['nose', 'rednose', 'coverage', 'mongomock']

setup(
    name='flask-mongoengine',
    version=metadata.__version__,
    url='https://github.com/mongoengine/flask-mongoengine',
    license='BSD',
    author='Ross Lawley',
    author_email='ross.lawley@gmail.com',
    test_suite='nose.collector',
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.8',
        'mongoengine>=0.8.0',
        'flask-wtf',
    ],
    packages=['flask_mongoengine',
              'flask_mongoengine.wtf'],
    include_package_data=True,
    tests_require=test_requirements,
    setup_requires=test_requirements,  # Allow proper nose usage with setuptools and tox
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
