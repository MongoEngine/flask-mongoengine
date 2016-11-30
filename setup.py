import os
from setuptools import setup


description = ('Flask-MongoEngine is a Flask extension '
               'that provides integration with MongoEngine and WTF model forms.')

# Load index.rst as long_description
doc_path = os.path.join(os.path.dirname(__file__), "docs", "index.rst")
long_description = open(doc_path).read()

# Stops exit traceback on tests
try:
    import multiprocessing # noqa
except:
    pass

test_requirements = ['coverage', 'nose', 'rednose']

setup(
    name='flask-mongoengine',
    version='0.8.1',
    url='https://github.com/mongoengine/flask-mongoengine',
    license='BSD',
    author='Ross Lawley',
    author_email='ross.lawley@gmail.com',
    test_suite='nose.collector',
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.8',
        'Flask-WTF>=0.13',
        'mongoengine>=0.8.0',
    ],
    packages=['flask_mongoengine',
              'flask_mongoengine.wtf'],
    include_package_data=True,
    tests_require=test_requirements,
    setup_requires=test_requirements,  # Allow proper nose usage with setuptools and tox
    description=description,
    long_description=long_description,
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
