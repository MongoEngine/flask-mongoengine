"""
Flask-MongoEngine
--------------

Flask support for MongoDB using MongoEngine.
Includes `WTForms`_ support.

Links
`````

* `development version
  <https://github.com/mongoengine/flask-mongoengine/raw/master#egg=Flask-MongoEngine-dev>`_

"""
from setuptools import setup

# Stops exit traceback on tests
try:
    import multiprocessing
except:
    pass

setup(
    name='flask-mongoengine',
    version='0.7.1',
    url='https://github.com/mongoengine/flask-mongoengine',
    license='BSD',
    author='Ross Lawley',
    author_email='ross.lawley@gmail.com',
    description='Flask support for MongoDB and with WTF model forms',
    long_description=__doc__,
    test_suite='nose.collector',
    zip_safe=False,
    platforms='any',
    install_requires=[
        'Flask>=0.8',
        'mongoengine>=0.7.10',
        'flask-wtf',
    ],
    packages=['flask_mongoengine',
              'flask_mongoengine.wtf'],
    include_package_data=True,
    tests_require=['nose', 'coverage'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
