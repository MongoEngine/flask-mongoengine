=============
Old changelog
=============

Changes in 1.0.0
================
Changelog maintenance automated and latest changelog available at
`github release page <https://github.com/MongoEngine/flask-mongoengine/releases>`_.

Use version 0.9.5 if old dependencies required.

Changes in 0.9.5
================
- Disable flake8 on travis.
- Correct `Except` clauses in code.
- Fix warning about undefined unicode variable in orm.py with python 3

Changes in 0.9.4
================
- ADDED: Support for `MONGODB_CONNECT` mongodb parameter (#321)
- ADDED: Support for `MONGODB_TZ_AWARE` mongodb parameter.

Changes in 0.9.3
================
- Fix test and mongomock (#304)
- Run Travis builds in a container-based environment (#301)

Changes in 0.9.2
================
- Travis CI/CD pipeline update to automatically publish 0.9.1.

Changes in 0.9.1
================
- Fixed setup.py for various platforms (#298).
- Added Flask-WTF v0.14 support (#294).
- MongoEngine instance now holds a reference to a particular Flask app it was
  initialized with (#261).

Changes in 0.9.0
================
- BREAKING CHANGE: Dropped Python v2.6 support

Changes in 0.8.2
================
- Fixed relying on mongoengine.python_support.
- Fixed cleaning up empty connection settings #285

Changes in 0.8.1
================

- Fixed connection issues introduced in 0.8
- Removed support for MongoMock

Changes in 0.8
==============

- Dropped MongoEngine 0.7 support
- Added MongoEngine 0.10 support
- Added PyMongo 3 support
- Added Python3 support up to 3.5
- Allowed empying value list in SelectMultipleField
- Fixed paginator issues
- Use InputRequired validator to allow 0 in required field
- Made help_text Field attribute optional
- Added "radio" form_arg to convert field into RadioField
- Added "textarea" form_arg to force conversion into TextAreaField
- Added field parameters (validators, filters...)
- Fixed 'False' connection settings ignored
- Fixed bug to allow multiple instances of extension
- Added MongoEngineSessionInterface support for PyMongo's tz_aware option
- Support arbitrary primary key fields (not "id")
- Configurable httponly flag for MongoEngineSessionInterface
- Various bugfixes, code cleanup and documentation improvements
- Move from deprecated flask.ext.* to flask_* syntax in imports
- Added independent connection handler for FlaskMongoEngine
- All MongoEngine connection calls are proxied via FlaskMongoEngine connection
  handler
- Added backward compatibility for settings key names
- Added support for MongoMock and temporary test DB
- Fixed issue with multiple DB support
- Various bugfixes

Changes in 0.7
==============
- Fixed only / exclude in model forms (#49)
- Added automatic choices coerce for simple types (#34)
- Fixed EmailField and URLField rendering and validation (#44, #9)
- Use help_text for field description (#43)
- Fixed Pagination and added Document.paginate_field() helper
- Keep model_forms fields in order of creation
- Added MongoEngineSessionInterface (#5)
- Added customisation hooks for FieldList sub fields (#19)
- Handle non ascii chars in the MongoDebugPanel (#22)
- Fixed toolbar stacktrace if a html directory is in the path (#31)
- ModelForms no longer patch Document.update (#32)
- No longer wipe field kwargs in ListField (#20, #19)
- Passthrough ModelField.save-arguments (#26)
- QuerySetSelectMultipleField now supports initial value (#27)
- Clarified configuration documentation (#33)
- Fixed forms when EmbeddedDocument has no default (#36)
- Fixed multiselect restore bug (#37)
- Split out the examples into a single file app and a cross file app

Changes in 0.6
==============
- Support for JSON and DictFields
- Speeding up QuerySetSelectField with big querysets

Changes in 0.5
==============
- Added support for all connection settings
- Fixed extended DynamicDocument

Changes in 0.4
==============
- Added CSRF support and validate_on_save via flask.ext.WTF
- Fixed DateTimeField not required

Changes in 0.3
===============
- Reverted mongopanel - got knocked out by a merge
- Updated imports paths

Changes in 0.2
===============
- Added support for password StringField
- Added ModelSelectMultiple

Changes in 0.1
===============
- Released to PyPi
