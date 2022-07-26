# Flask-WTF(WTForms) integration

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

```{warning}
As at version **2.0.0** there is no {attr}`wtf_validators` duplicates/conflicts check.
User should be careful with manual {attr}`wtf_validators` setup. And in case of forms
problems this is first place to look on.

{attr}`wtf_validators` and {attr}`wtf_filters` duplication check expected in future
versions; PRs are welcome.
```

Some additional transformations are made by specific field, check exact field
documentation below for more info.

## Supported fields

### BinaryField

Not yet documented. Please help us with new pull request.

### BooleanField

Not yet documented. Please help us with new pull request.

### DateField

Not yet documented. Please help us with new pull request.

### DateTimeField

Not yet documented. Please help us with new pull request.

### DecimalField

Not yet documented. Please help us with new pull request.

### DictField

Not yet documented. Please help us with new pull request.

### EmailField

Not yet documented. Please help us with new pull request.

### EmbeddedDocumentField

Not yet documented. Please help us with new pull request.

### FileField

Not yet documented. Please help us with new pull request.

### FloatField

Not yet documented. Please help us with new pull request.

### IntField

Not yet documented. Please help us with new pull request.

### ListField

Not yet documented. Please help us with new pull request.

### ReferenceField

Not yet documented. Please help us with new pull request.

### SortedListField (partly?)

Not yet documented. Please help us with new pull request.

### StringField

Not yet documented. Please help us with new pull request.

### URLField

Not yet documented. Please help us with new pull request.

## Unsupported fields

### CachedReferenceField

Not yet documented. Please help us with new pull request.

### ComplexDateTimeField

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
[supported fields]: #supported-fields
[#379]: https://github.com/MongoEngine/flask-mongoengine/issues/379
[integration]: forms
[global transforms]: #global-transforms
