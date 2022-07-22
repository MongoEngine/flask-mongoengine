# Model and forms fields definition

## Supported fields

Flask-Mongoengine support all database fields definition. Even if there will be some
new field type created in parent [mongoengine] project, we will silently bypass
field definition to it, if we do not declare rules on our side.

```{note}
Version **2.0.0** Flask-Mongoengine update support [mongoengine] fields, based on
version **mongoengine==0.21**. Any new fields bypassed without modification.
```

## Keyword only definition

```{eval-rst}
.. versionchanged:: 2.0.0
```

Database model definition rules and Flask-WTF/WTForms integration was seriously
updated in version **2.0.0**. Unfortunately, these changes implemented without any
deprecation stages.

Before version **2.0.0** Flask-Mongoengine integration allowed to pass fields
parameters as arguments. To exclude any side effects or keyword parameters
duplication/conflicts, since version **2.0.0** all [supported fields] require keyword
only setup.

Such approach removes number of issues and questions, when users frequently used
Flask-WTF/WTForms definition rules by mistake, or just missed that some arguments
was passed to keyword places silently creating unexpected side effects. You can
check issue [#379] as example of one of such cases.

## Flask-WTF(WTForms) integration

Flask-Mongoengine and Flask-WTF/WTForms are heavily integrated, to reduce amount of
boilerplate code, required to make database model and online form. In the same time
a lot of options was created to keep extreme flexibility.

After database model definition user does not require to repeat same code in form
definition, instead it is possible to use integrated converter, that will do most of
the work.

Flask-Mongoengine will transform some model's properties to Flask-WTF/WTForms
validators, so user does not need to care about standards. For full list of
transformations, please review specific field documentation.

In the same time, user is able to extend database fields definition with
specific `filters` and `validators`, that will be implemented in form.

For complex or custom cases user can bypass additional Flask-WTF/WTForms fields
arguments , on form generation with {func}`~.model_form` as {attr}`field_args`
parameter.

For extremely complex cases, or cases when some field not yet supported by
Flask-Mongoengine user is able to implement special database model field with
completely independent field converter for forms, that will be used, ignoring
Flask-Mongoengine internals. To do this:

1. Inherit from database model field type.
2. Implement {func}`to_form_field` method with additional {attr}`model`,
   {attr}`field_args` arguments, that will return form field. Check
   {attr}`.ModelConverter.convert` first lines for details.

```{note}
{func}`to_form_field` was undocumented feature, even before **2.0.0**, but was not
in priority of {attr}`.ModelConverter.convert` execution order. I.e. some
transformations was made before this function existance check, even full form field
could be generated in some cases.
```

```{warning}
Usage of {func}`to_form_field` approach assume that there will not be any
tranformation from Flask-Mongongine side. So user is fully rsponsible for all
validators, labels, etc.
```

### Global transforms

For all fields, processed by Flask-Mongoengine integration:

- If model field definition have {attr}`validators` defined, they will be forwarded to
  WTForm as {attr}`validators`. This is not protection from {attr}`validators`
  extension by Flask-Mongoengine.
- If model field definition have {attr}`filters` defined, they will be forwarded to
  WTForm as {attr}`filters`.
- If model field definition have {attr}`required`, then {class}`~wtforms.validators.InputRequired`
  will be added to form {attr}`validators`, otherwise {class}`~wtforms.validators.Optional`
  added.
- If model field definition have {attr}`verbose_name` it will be used as form field
  {attr}`label`, otherwise pure field name used.
- If model field definition have {attr}`help_text` it will be used as form field
  {attr}`description`, otherwise empty string used.
- Field's {attr}`default` used as form {attr}`default`, that's why for string fields
  special {class}`~.NoneStringField` with `None` value support used.
- Field's {attr}`choices`, if exist, used as form {attr}`choices`.

Some additional transformations are made by specific field, check exact field
documentation below for more info.

### Supported fields

- BinaryField
- BooleanField
- DateField
- DateTimeField
- DecimalField
- DictField
- EmailField
- EmbeddedDocumentField
- FileField
- FloatField
- IntField
- ListField
- ReferenceField
- SortedListField (partly?)
- StringField
- URLField

### Unsupported fields

- CachedReferenceField
- ComplexDateTimeField
- DynamicField
- EmbeddedDocumentListField
- EnumField
- GenericEmbeddedDocumentField
- GenericLazyReferenceField
- GeoJsonBaseField
- GeoPointField
- ImageField
- LazyReferenceField
- LineStringField
- LongField
- MapField
- MultiLineStringField
- MultiPointField
- MultiPolygonField
- PointField
- PolygonField
- SequenceField
- UUIDField

### Unsure

- GenericReferenceField
- ObjectIdField

[mongoengine]: https://docs.mongoengine.org/
[supported fields]: #supported-fields
[#379]: https://github.com/MongoEngine/flask-mongoengine/issues/379
