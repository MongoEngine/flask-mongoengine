# Migration to 2.0.0 and changes

## Empty fields are not created in database

If you are already aware about empty string vs `None` database conflicts, you should
know that some string based generated forms behaviour are not consistent between
version **<=1.0.0** and **2.0.0+**.

In version **2.0.0** all fields with empty strings will be considered as `None` and
will not be saved by default (this is easy to change for particular field to keep
old behaviour for existed projects).

This behaviour is different from previous versions, where
{class}`~flask_mongoengine.db_fields.StringField` consider empty string as valid
value, and save it to database. This is the opposite behavior against original
[mongoengine] project and related database.

```{warning}
To keep easy migration and correct deprecation steps {func}`~.model_form` and
{func}`.model_fields` still keep old behaviour.
```

To be completely clear, let look on example. Let make a completely meaningless model,
with all field types from [mongoengine], like this:

```python
"""example_app.models.py"""
from flask_mongoengine import MongoEngine

db = MongoEngine()


class Todo(db.Document):
    """Test model for AllFieldsModel."""
    string = db.StringField()


class Embedded(db.EmbeddedDocument):
    """Test embedded for AllFieldsModel."""
    string = db.StringField()


class AllFieldsModel(db.Document):
    """Meaningless Document with all field types."""
    binary_field = db.BinaryField()
    boolean_field = db.BooleanField()
    date_field = db.DateField()
    date_time_field = db.DateTimeField()
    decimal_field = db.DecimalField()
    dict_field = db.DictField()
    email_field = db.EmailField()
    embedded_document_field = db.EmbeddedDocumentField(document_type=Embedded)
    file_field = db.FileField()
    float_field = db.FloatField()
    int_field = db.IntField()
    list_field = db.ListField(field=db.StringField)
    reference_field = db.ReferenceField(document_type=Todo)
    sorted_list_field = db.SortedListField(field=db.StringField)
    string_field = db.StringField()
    url_field = db.URLField()
    cached_reference_field = db.CachedReferenceField(document_type=Todo)
    complex_date_time_field = db.ComplexDateTimeField()
    dynamic_field = db.DynamicField()
    embedded_document_list_field = db.EmbeddedDocumentListField(document_type=Embedded)
    enum_field = db.EnumField(enum=[1, 2])
    generic_embedded_document_field = db.GenericEmbeddedDocumentField()
    generic_lazy_reference_field = db.GenericLazyReferenceField()
    geo_json_base_field = db.GeoJsonBaseField()
    geo_point_field = db.GeoPointField()
    image_field = db.ImageField()
    lazy_reference_field = db.LazyReferenceField(document_type=Todo)
    line_string_field = db.LineStringField()
    long_field = db.LongField()
    map_field = db.MapField(field=db.StringField())
    multi_line_string_field = db.MultiLineStringField()
    multi_point_field = db.MultiPointField()
    multi_polygon_field = db.MultiPolygonField()
    point_field = db.PointField()
    polygon_field = db.PolygonField()
    sequence_field = db.SequenceField()
    uuid_field = db.UUIDField()
    generic_reference_field = db.GenericReferenceField(document_type=Todo)
    object_id_field = db.ObjectIdField()
```

Now let's make an example instance of such object and save it to db.

```python
from example_app.models import AllFieldsModel

obj = AllFieldsModel()
obj.save()
```

On database side this document will be created:

```json
{
    "_id": {
        "$oid": "62df93ac3fe82c8656aae60d"
    },
    "dict_field": {},
    "list_field": [],
    "sorted_list_field": [],
    "embedded_document_list_field": [],
    "map_field": {},
    "sequence_field": 1
}
```

For empty form Flask-Mongoengine **2.0.0** will create exactly the same document,
old project version will try to fill some fields, based on
{class}`~flask_mongoengine.db_fields.StringField`.

[mongoengine]: https://docs.mongoengine.org/
