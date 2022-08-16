# WTForms integration

```{important}
Documentation below is related to project version 2.0.0 or higher, old versions has
completely different approach for forms generation.

And despite the fact that the old code is included in version 2.0.0 to keep correct
deprecation workflow (where possible), it is not documented (and was not) and not
maintained.

If you faced any forms problems, consider migration to new methods and approach.
```

Flask-Mongoengine and Flask-WTF/WTForms are heavily integrated, to reduce amount of
boilerplate code, required to make database model and online form. In the same time
a lot of options was created to keep extreme flexibility.

After database model definition user does not require to repeat same code in form
definition, instead it is possible to use integrated converter, that will do most of
the work.

Flask-Mongoengine will transform some model's properties to Flask-WTF/WTForms
validators, so user does not need to care about standards. For full list of
transformations, please review [global transforms] and specific field documentation
below.

In the same time, user is able to adjust database fields definition with
specific settings as on stage of Document model definition, as on form generation stage.
This allows to create several forms for same model, for different circumstances.

## Requirements

For correct integration behavior several requirements should be met:

- Document classes should be used from Flask-Mongoengine
  {class}`flask_mongoengine.MongoEngine` class, or from
  {mod}`flask_mongoengine.documents` module.
- Document classes should be used from Flask-Mongoengine
  {class}`flask_mongoengine.MongoEngine` class, or from
  {mod}`flask_mongoengine.db_fields` module.

## Global transforms

For all fields, processed by Flask-Mongoengine integration:

- If model field definition have {attr}`wtf_validators` defined, they will be
  forwarded to WTForm as {attr}`validators`. This is not protection from
  {attr}`validators` extension by Flask-Mongoengine.
- If model field definition have {attr}`wtf_filters` defined, they will be forwarded to
  WTForm as {attr}`filters`.
- If model field definition have {attr}`required`, then
  {class}`~wtforms.validators.InputRequired`
  will be added to form {attr}`validators`, otherwise
  {class}`~wtforms.validators.Optional`
  added.
- If model field definition have {attr}`verbose_name` it will be used as form field
  {attr}`label`, otherwise pure field name used.
- If model field definition have {attr}`help_text` it will be used as form field
  {attr}`description`, otherwise empty string used.
- Field's {attr}`default` used as form {attr}`default`, that's why special WTForms
  fields implementations was created. Details can be found in
  {mod}`flask_mongoengine.wtf.fields` module. In new form generator only 'Mongo'
  prefixed classes are used for fields, other classes are deprecated and will be
  removed in version **3.0.0**. If you have own nesting classes, you should check
  inheritance and make an update.
- Field's {attr}`choices`, if exist, used as form {attr}`choices`.

```{warning}
As at version **2.0.0** there is no {attr}`wtf_validators` duplicates/conflicts check.
User should be careful with manual {attr}`wtf_validators` setup. And in case of forms
problems this is first place to look on.

{attr}`wtf_validators` and {attr}`wtf_filters` duplication check expected in future
versions; PRs are welcome.
```

Some additional transformations are made by specific field, check exact field
documentation below for more info.

## BinaryField

Not yet documented. Please help us with new pull request.

## BooleanField

- API: {class}`.db_fields.BooleanField`
- Default form field class: {class}`~.MongoBooleanField`

### Form generation behaviour

BooleanField is very complicated in terms of Mongo database support. In
Flask-Mongoengine before version **2.0.0+** database BooleanField used
{class}`wtforms.fields.BooleanField` as form representation, this raised several not
clear problems, that was related to how {class}`wtforms.fields.BooleanField` parse
and work with form values. Known problems in version, before **2.0.0+**:

- Default value of field, specified in database definition was ignored, if default
  is `None` and nulls allowed, i.e. {attr}`null=True` (Value was always `False`).
- Field was always created in database document, even if not checked, as there is
  impossible to split `None` and `False` values, when only checkbox available.

To fix all these issues, and do not create database field by default, Flask-Mongoengine
**2.0.0+** uses dropdown field by default.

By default, database BooleanField not allowing `None` value, meaning that field can
be `True`, `False` or not created in database at all. If database field configuration
allowing `None` values, i.e. {attr}`null=True`, then, when nothing selected in
dropdown, the field will be created with `None` value.

```{important}
It is responsobility of developer, to correctly setup database field definition and
make proper tests before own application release. BooleanField can create unexpected
application behavior in if checks. Developer, should recheck all if checks like:

- `if filed_value:` this will match `True` database value
- `if not filed_value:` this will match `False` or `None` database value or not existing
  document key
- `if field_value is None:` this will match `None` database value or not existing
  document key
- `if field_value is True:` this will match `True` database value
- `if field_value is False:` this will match `False` database value
- `if field_value is not None:` this will match `True`, `False` database value
- `if field_value is not True:` this will match `False`, `None` database value or not
  existing document key
- `if filed_value is not False:` this will match `True`, `None` database value or not
  existing document key
```

### Examples

#### BooleanField with default dropdown

Such definition will not create any field in document, if dropdown not selected.

```python
"""boolean_demo.py"""
from example_app.models import db


class BooleanDemoModel(db.Document):
    """Documentation example model."""

    boolean_field = db.BooleanField()
```

#### BooleanField with allowed `None` value

Such definition will create document field, even if nothing selected. The value will
be `None`. If, during edit, `yes` or `no` dropdown values replaced to `---`, then
saved value in document will be also changed to `None`.

By default, `None` value represented as `---` text in dropdown.

```python
"""boolean_demo.py"""
from example_app.models import db


class BooleanDemoModel(db.Document):
    """Documentation example model."""

    boolean_field_with_null = db.BooleanField(null=True)
```

#### BooleanField with replaced dropdown text

Dropdown text can be easily replaced, there is only one requirement: New choices,
should be correctly coerced by {func}`~.coerce_boolean`, or function should be
replaced too.

```python
"""boolean_demo.py"""
from example_app.models import db


class BooleanDemoModel(db.Document):
    """Documentation example model."""

    boolean_field_with_as_choices_replace = db.BooleanField(
        wtf_options={
            "choices": [("", "Not selected"), ("yes", "Positive"), ("no", "Negative")]
        }
    )

```

#### BooleanField with default `True` value, but with allowed nulls

```python
"""boolean_demo.py"""
from example_app.models import db


class BooleanDemoModel(db.Document):
    """Documentation example model."""

    true_boolean_field_with_allowed_null = db.BooleanField(default=True, null=True)
```

## ComplexDateTimeField

- API: {class}`.db_fields.ComplexDateTimeField`
- Default form field class: {class}`wtforms.fields.DateTimeLocalField`

### Form generation behaviour

ComplexDateTimeField stores date and time information in database `string` format. This
format allow precision up to microseconds dimension.

Unfortunately, there is no HTML5 field, that allow so high precision. That's why, by
default the generated field will use HTML5 `<input type="datetime-local">` with
precision set to milliseconds.

If you require concrete microseconds for edit purposes, please use
{class}`wtforms.fields.DateTimeField` with correct format (see examples below).

Field is easy adjustable, to use any other precision. Check examples and example app
for more details.

### Examples

dates_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

#### ComplexDateTimeField with milliseconds precision

```python
"""dates_demo.py"""
from example_app.models import db


class DateTimeModel(db.Document):
    """Documentation example model."""

    complex_datetime = db.ComplexDateTimeField()
```

#### ComplexDateTimeField with seconds precision

```python
"""dates_demo.py"""
from example_app.models import db


class DateTimeModel(db.Document):
    """Documentation example model."""

    complex_datetime_sec = db.ComplexDateTimeField(
        wtf_options={"render_kw": {"step": "1"}}
    )
```

#### ComplexDateTimeField with microseconds precision (text)

```python
"""dates_demo.py"""
from wtforms.fields import DateTimeField

from example_app.models import db


class DateTimeModel(db.Document):
    """Documentation example model."""

    complex_datetime_microseconds = db.ComplexDateTimeField(
        wtf_field_class=DateTimeField, wtf_options={"format": "%Y-%m-%d %H:%M:%S.%f"}
    )
```

## DateField

- API: {class}`.db_fields.DateField`
- Default form field class: {class}`wtforms.fields.DateField`

### Form generation behaviour

DateField is one of the simplest fields in the forms generation process. By default,
the field use {class}`wtforms.fields.DateField` WTForms class, representing a form
input with standard HTML5 `<input type="date">`. No custom additional transformation
done, during field generation. Field is fully controllable by [global transforms].

### Examples

dates_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

#### Not limited DateField

```python
"""dates_demo.py"""
from example_app.models import db


class DateTimeModel(db.Document):
    """Documentation example model."""

    date = db.DateField()
```

## DateTimeField

- API: {class}`.db_fields.DateTimeField`
- Default form field class: {class}`wtforms.fields.DateTimeLocalField`

### Form generation behaviour

DateTimeField stores date and time information in database `date` format. This
format allow precision up to milliseconds dimension. By default, generated form will
use HTML5 `<input type="datetime-local">` with precision set to seconds.

Field is easy adjustable, to use any other precision. Check examples and example app
for more details.

It is possible to use {class}`wtforms.fields.DateTimeField` for text input behaviour.

### Examples

dates_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

#### DateTimeField with seconds precision

```python
"""dates_demo.py"""
from example_app.models import db


class DateTimeModel(db.Document):
    """Documentation example model."""

    datetime = db.DateTimeField()
```

#### DateTimeField without seconds

```python
"""dates_demo.py"""
from example_app.models import db


class DateTimeModel(db.Document):
    """Documentation example model."""

    datetime_no_sec = db.DateTimeField(wtf_options={"render_kw": {"step": "60"}})
```

#### DateTimeField with milliseconds precision

```python
"""dates_demo.py"""
from example_app.models import db


class DateTimeModel(db.Document):
    """Documentation example model."""

    datetime_ms = db.DateTimeField(wtf_options={"render_kw": {"step": "0.001"}})
```

## DecimalField

- API: {class}`.db_fields.DecimalField`
- Default form field class: {class}`wtforms.fields.DecimalField`

### Form generation behaviour

From form generation side this field is pretty standard and do not use any form
generation adjustments.

If database field definition has any of {attr}`min_value` or {attr}`max_value`, then
{class}`~wtforms.validators.NumberRange` validator will be added to form field.

### Examples

numbers_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

#### Not limited DecimalField

```python
"""numbers_demo.py"""
from example_app.models import db


class NumbersDemoModel(db.Document):
    """Documentation example model."""

    decimal_field_unlimited = db.DecimalField()
```

#### Limited DecimalField

```python
"""numbers_demo.py"""
from decimal import Decimal

from example_app.models import db


class NumbersDemoModel(db.Document):
    """Documentation example model."""

    decimal_field_limited = db.DecimalField(
        min_value=Decimal("1"), max_value=Decimal("200.455")
    )
```

## DictField

- API: {class}`.db_fields.DictField`
- Default form field class: {class}`~.MongoDictField`

DictField has `Object` type in terms of Mongo database itself, so basically it defines
document inside document, but without pre-defined structure. That's why this is one
of fields, that has default value specified inside Mongoengine itself, and that's
why is always (almost) created.

The developer should understand that database keyword argument {attr}`default` is
forwarded to form by default, but can be separately overwritten in form. This brings
a lot of options for form field configuration.

Also, should be additionally noted that database `Null` value in form is represented as
empty string. Non-existing field is represented with form {attr}`default` for new
forms (without instance inside) or with empty string for non-empty forms.

Complicated? Probably. That's why this field was completely rewritten in version
**2.0.0**. Check examples, and everything will be clear.

### Form generation behaviour

Our default form generation follow Mongoengine internals and will use database field
default (empty dict) to populate to new form or to not filled field in existing form.

In the same time, we are allowing extending of this behaviour, and not creating
field in database, if default value provided as `None`. In this case, generated
field for new form will be empty, without any pre-filled value.

Same empty field will be displayed in case, when both {attr}`default=None` and
{attr}`null=True` selected, during database form initialization. In this case form
field will be empty, without any placeholder, but on save `null` object will be
created in document.

Also, we even support separated defaults for form field and database field, allowing
any form+database behaviour.

### Examples

#### DictField with default empty dict value

Will place `{}` to form for existing/new fields. This value is hardcodded in parent
MongoEngine project.

```python
"""dict_demo.py"""
from example_app.models import db


class DictDemoModel(db.Document):
    """Documentation example model."""

    dict_field = db.DictField()
```

#### DictField with default `None` value, ignored by database

Reminder: Such field is empty in form, and will not create anything in database if
not filled.

```python
"""dict_demo.py"""
from example_app.models import db


class DictDemoModel(db.Document):
    """Documentation example model."""

    no_dict_field = db.DictField(default=None)
```

#### DictField with default `None` value, saved to database

Reminder: Such field is empty in form, and will create `null` object in database if
not filled.

```python
"""dict_demo.py"""
from example_app.models import db


class DictDemoModel(db.Document):
    """Documentation example model."""

    null_dict_field = db.DictField(default=None, null=True)
```

#### DictField with pre-defined default dict

This value is pre-defined on database level. So behaviour of form and in-code
creation of such objects will be the same - default dict will be saved to database,
if nothing provided to form/instance. Form will be pre-filled with default dict.

```python
"""dict_demo.py"""
from example_app.models import db


def get_default_dict():
    """Example of default dict specification."""
    return {"alpha": 1, "text": "text", "float": 1.2}


class DictDemoModel(db.Document):
    """Documentation example model."""

    dict_default = db.DictField(default=get_default_dict)
```

#### DictField with pre-defined value and no document object creation on `Null`

This is a case when you do not want to create any record in database document, if
user completely delete pre-filled value in new document form. Here we use different
`null` and `default` values in form field generation and during database object
generation.

```python
"""dict_demo.py"""
from example_app.models import db


def get_default_dict():
    """Example of default dict specification."""
    return {"alpha": 1, "text": "text", "float": 1.2}


class DictDemoModel(db.Document):
    """Documentation example model."""

    no_dict_prefilled = db.DictField(
        default=None,
        null=False,
        wtf_options={"default": get_default_dict, "null": True},
    )
```

#### DictField with pre-defined default dict with `Null` fallback

This is very rare case, when some default value is given, meaning that this
value will be populated to the field, but if completely deleted, than `Null` will be
saved in database.

```python
"""dict_demo.py"""
from example_app.models import db


def get_default_dict():
    """Example of default dict specification."""
    return {"alpha": 1, "text": "text", "float": 1.2}


class DictDemoModel(db.Document):
    """Documentation example model."""

    null_dict_default = db.DictField(default=get_default_dict, null=True)
```

## EmailField

- API: {class}`.db_fields.EmailField`
- Default form field class: {class}`~.MongoEmailField`

### Form generation behaviour

Unlike [StringField] WTForm class of the field is not adjusted by normal form
generation sequence and always match {class}`~.MongoEmailField`. All other
adjustments, related to validators insert are work with EmailField in the same way,
as in [StringField].

Additional {class}`~wtforms.validators.Email` validator is also inserted to form
field, to exclude unnecessary database request, if form data incorrect.

Field respect user's adjustments in {attr}`wtf_field_class` option of
{class}`.db_fields.EmailField`. This will change form field display, but will not
change inserted validators.

### Examples

strings_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

#### Not required EmailField

```python
"""strings_demo.py"""
from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    url_field = db.EmailField()
````

#### Required EmailField

```python
"""strings_demo.py"""
from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    required_url_field = db.EmailField(required=True)
````

## EmbeddedDocumentField

Not yet documented. Please help us with new pull request.

## FileField

Not yet documented. Please help us with new pull request.

## FloatField

```{versionchanged} 2.0.0
Default form field class changed from: {class}`wtforms.fields.FloatField` to
{class}`~.fields.MongoFloatField`.
```

- API: {class}`.db_fields.FloatField`
- Default form field class: {class}`~.fields.MongoFloatField`

### Form generation behaviour

For Mongo database {class}`~.db_fields.FloatField` special WTForm field was created.
This field's behaviour is the same, as for {class}`wtforms.fields.FloatField`,
but the widget is replaced to {class}`~wtforms.widgets.NumberInput`, this should make a
look of generated form better. It is possible, that in some cases usage of base,
{class}`wtforms.fields.FloatField` can be required by form design. Both fields are
completely compatible, and replace can be done with {attr}`wtf_field_class` db form
parameter.

If database field definition has any of {attr}`min_value` or {attr}`max_value`, then
{class}`~wtforms.validators.NumberRange` validator will be added to form field.

### Examples

numbers_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

#### Not limited FloatField

```python
"""numbers_demo.py"""
from example_app.models import db


class NumbersDemoModel(db.Document):
    """Documentation example model."""

    float_field_unlimited = db.FloatField()
```

#### Limited FloatField

```python
"""numbers_demo.py"""
from example_app.models import db


class NumbersDemoModel(db.Document):
    """Documentation example model."""

    float_field_limited = db.FloatField(min_value=float(1), max_value=200.455)
```

## IntField

- API: {class}`.db_fields.IntField`
- Default form field class: {class}`wtforms.fields.IntegerField`

### Form generation behaviour

From form generation side this field is pretty standard and do not use any form
generation adjustments.

If database field definition has any of {attr}`min_value` or {attr}`max_value`, then
{class}`~wtforms.validators.NumberRange` validator will be added to form field.

### Examples

numbers_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

#### Not limited IntField

```python
"""numbers_demo.py"""
from example_app.models import db


class NumbersDemoModel(db.Document):
    """Documentation example model."""

    integer_field_unlimited = db.IntField()
```

#### Limited IntField

```python
"""numbers_demo.py"""
from example_app.models import db


class NumbersDemoModel(db.Document):
    """Documentation example model."""

    integer_field_limited = db.IntField(min_value=1, max_value=200)
```

## ListField

Not yet documented. Please help us with new pull request.

## ReferenceField

Not yet documented. Please help us with new pull request.

## SortedListField (partly?)

Not yet documented. Please help us with new pull request.

## StringField

- API: {class}`.db_fields.StringField`
- Default form field class: Selected by field settings combination

### Form generation behaviour

By default, during WTForm generation for fields without specified size (
{attr}`min_length` or {attr}`max_length`) class {class}`.MongoTextAreaField` is used,
in case when {attr}`min_length` or {attr}`max_length` set, then
{class}`.MongoStringField` used and {class}`~wtforms.validators.Length` will be added
to form field validators. This allows to keep documents of any size in mongodb.

In some cases class {class}`~.MongoStringField` is not the best choice for field, even
with limited size. In this case user can easily overwrite generated field class by
providing {attr}`wtf_field_class` on {class}`.db_fields.StringField` field declaration,
as on document, as well as on form generation steps.

If database field definition has {attr}`regex` parameter set, then
{class}`~wtforms.validators.Regexp` validator will be added to the form field.

### Features deprecated

Field declaration step keyword arguments {attr}`password` and {attr}`textarea` are
deprecated in Flask-Mongoengine version **2.0.0** and exist only to make migration
steps easy.

To implement same behaviour, user should use {attr}`wtf_field_class` setting on
{class}`.db_fields.StringField` init.

### Related WTForm custom fields

Several special WTForms field implementation was created to support mongodb database
behaviour and do not create any values in database, in case of empty fields. They
can be used as {attr}`wtf_field_class` setting or independently. Some of them used
in another database fields too, but all of them based on
{class}`wtforms.fields.StringField` and {class}`~.EmptyStringIsNoneMixin`. You can use
{class}`~.EmptyStringIsNoneMixin` for own field types.

- {class}`~.MongoEmailField`
- {class}`~.MongoHiddenField`
- {class}`~.MongoPasswordField`
- {class}`~.MongoSearchField`
- {class}`~.MongoStringField`
- {class}`~.MongoTelField`
- {class}`~.MongoTextAreaField`
- {class}`~.MongoURLField`

### Examples

strings_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

#### Not limited StringField as MongoTextAreaField

```python
"""strings_demo.py"""
from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    string_field = db.StringField()
```

#### Not limited StringField as MongoTelField

```python
"""strings_demo.py"""
from example_app.models import db
from flask_mongoengine.wtf import fields as mongo_fields


class StringsDemoModel(db.Document):
    """Documentation example model."""

    tel_field = db.StringField(wtf_field_class=mongo_fields.MongoTelField)
```

#### Not limited StringField as MongoTextAreaField with https regex

[mongoengine] and [wtforms] projects are not consistent in how they work with regex.
You will be safe, if you use {func}`re.compile` each time, when you work with regex
settings, before parent projects itself.

```python
"""strings_demo.py"""
import re

from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    regexp_string_field = db.StringField(regex=re.compile(
        r"^(https:\/\/)[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=]+$"
    ))
```

#### Size limited StringField as MongoStringField

```python
"""strings_demo.py"""
from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    sized_string_field = db.StringField(min_length=5)
```

#### Required password field with minimum size

```python
"""strings_demo.py"""
from example_app.models import db
from flask_mongoengine.wtf import fields as mongo_fields


class StringsDemoModel(db.Document):
    """Documentation example model."""

    password_field = db.StringField(
        wtf_field_class=mongo_fields.MongoPasswordField,
        required=True,
        min_length=5,
    )
```

## URLField

- API: {class}`.db_fields.URLField`
- Default form field class: {class}`~.MongoURLField`

### Form generation behaviour

Unlike [StringField] WTForm class of the field is not adjusted by normal form
generation sequence and always match {class}`~.MongoURLField`. All other
adjustments, related to validators insert are work with EmailField in the same way,
as in [StringField].

Additional {class}`~wtforms.validators.Regexp` validator is also inserted to form
field, to exclude unnecessary database request, if form data incorrect. This
validator use regexp, provided in {attr}`url_regex` of {class}`.db_fields.URLField`,
or default URL regexp from [mongoengine] project. This is different from
Flask-Mongoengine version **1.0.0** or earlier, where {class}`~wtforms.validators.URL`
was inserted. This was changed, to exclude validators conflicts.

```{important}
{func}`~.model_form` is still use {class}`~wtforms.validators.URL` for
compatibility with old setups.
```

Field respect user's adjustments in {attr}`wtf_field_class` option of
{class}`.db_fields.URLField`. This will change form field display, but will not
change inserted validators.

### Examples

strings_demo.py in example app contain basic non-requirement example. You can adjust
it to any provided example for test purposes.

#### Not required URLField

```python
"""strings_demo.py"""
from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    url_field = db.URLField()
````

#### Required URLField with minimum size

```python
"""strings_demo.py"""
from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    required_url_field = db.URLField(required=True, min_length=25)
````

#### URLField with https only regexp check, if data exist

Regexp for {attr}`url_regex` should be prepared by {mod}`re`.

```python
"""strings_demo.py"""
import re

from example_app.models import db


class StringsDemoModel(db.Document):
    """Documentation example model."""

    https_url_field = db.URLField(
        url_regex=re.compile(
            r"^(https:\/\/)[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=]+$"
        ),
    )
````

## Unsupported fields

### CachedReferenceField

Not yet documented. Please help us with new pull request.

### DynamicField

Not yet documented. Please help us with new pull request.

### EmbeddedDocumentListField

Not yet documented. Please help us with new pull request.

### EnumField

Not yet documented. Please help us with new pull request.

### GenericEmbeddedDocumentField

Not yet documented. Please help us with new pull request.

### GenericLazyReferenceField

Not yet documented. Please help us with new pull request.

### GeoJsonBaseField

Not yet documented. Please help us with new pull request.

### GeoPointField

Not yet documented. Please help us with new pull request.

### ImageField

Not yet documented. Please help us with new pull request.

### LazyReferenceField

Not yet documented. Please help us with new pull request.

### LineStringField

Not yet documented. Please help us with new pull request.

### LongField

Not yet documented. Please help us with new pull request.

### MapField

Not yet documented. Please help us with new pull request.

### MultiLineStringField

Not yet documented. Please help us with new pull request.

### MultiPointField

Not yet documented. Please help us with new pull request.

### MultiPolygonField

Not yet documented. Please help us with new pull request.

### PointField

Not yet documented. Please help us with new pull request.

### PolygonField

Not yet documented. Please help us with new pull request.

### SequenceField

Not yet documented. Please help us with new pull request.

### UUIDField

Not yet documented. Please help us with new pull request.

## Unsure

### GenericReferenceField

Not yet documented. Please help us with new pull request.

### ObjectIdField

Not yet documented. Please help us with new pull request.

[mongoengine]: https://docs.mongoengine.org/

[#379]: https://github.com/MongoEngine/flask-mongoengine/issues/379

[integration]: forms

[global transforms]: #global-transforms

[stringfield]: #stringfield

[wtforms]: https://wtforms.readthedocs.io/en/3.0.x/
