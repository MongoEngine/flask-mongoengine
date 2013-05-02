=========
Changelog
=========

Changes in 0.7
==============
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
