"""Integration tests for new WTForms generation in Flask-Mongoengine 2.0."""
import json

import pytest
from werkzeug.datastructures import MultiDict

wtforms = pytest.importorskip("wtforms")


@pytest.fixture()
def local_app(app):
    """Helper fixture to minimize code indentation."""
    with app.test_request_context("/"):
        yield app


def test__full_document_form__does_not_create_any_unexpected_data_in_database(db):
    """
    Test to ensure that we are following own promise in documentation, read:
    http://docs.mongoengine.org/projects/flask-mongoengine/en/latest/migration_to_v2.html#empty-fields-are-not-created-in-database
    """

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
        embedded_document_list_field = db.EmbeddedDocumentListField(
            document_type=Embedded
        )
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

    AllFieldsModelForm = AllFieldsModel.to_wtf_form()
    form = AllFieldsModelForm(
        MultiDict(
            {
                "binary_field": "",
                "boolean_field": "",
                "date_field": "",
                "date_time_field": "",
                "decimal_field": "",
                "dict_field": "",
                "email_field": "",
                "embedded_document_field": "",
                "file_field": "",
                "float_field": "",
                "int_field": "",
                "list_field": "",
                "reference_field": "",
                "sorted_list_field": "",
                "string_field": "",
                "url_field": "",
                "cached_reference_field": "",
                "complex_date_time_field": "",
                "dynamic_field": "",
                "embedded_document_list_field": "",
                "enum_field": "",
                "generic_embedded_document_field": "",
                "generic_lazy_reference_field": "",
                "geo_json_base_field": "",
                "geo_point_field": "",
                "image_field": "",
                "lazy_reference_field": "",
                "line_string_field": "",
                "long_field": "",
                "map_field": "",
                "multi_line_string_field": "",
                "multi_point_field": "",
                "multi_polygon_field": "",
                "point_field": "",
                "polygon_field": "",
                "sequence_field": "",
                "uuid_field": "",
                "generic_reference_field": "",
                "object_id_field": "",
            }
        )
    )
    assert form.validate()
    form.save()

    obj = AllFieldsModel.objects.get(id=form.instance.pk)
    object_dict = json.loads(obj.to_json())
    object_dict.pop("_id")

    assert object_dict == {
        "dict_field": {},
        "list_field": [],
        "sorted_list_field": [],
        "embedded_document_list_field": [],
        "map_field": {},
        "sequence_field": 1,
    }
