"""Integration tests for new WTForms generation in Flask-Mongoengine 2.0."""
import json

import pytest
from werkzeug.datastructures import MultiDict

wtforms = pytest.importorskip("wtforms")
from wtforms import fields as wtf_fields  # noqa
from wtforms import widgets as wtf_widgets  # noqa

from flask_mongoengine.wtf import fields as mongo_fields  # noqa


@pytest.fixture()
def local_app(app):
    """Helper fixture to minimize code indentation."""
    with app.test_request_context("/"):
        yield app


@pytest.mark.parametrize(
    ["value", "expected_value"],
    [
        ("", None),
        ("none", None),
        ("nOne", None),
        ("None", None),
        ("null", None),
        (None, None),
        ("no", False),
        ("N", False),
        ("n", False),
        ("false", False),
        ("False", False),
        (False, False),
        ("yes", True),
        ("y", True),
        ("true", True),
        (True, True),
    ],
)
def test_coerce_boolean__return_correct_value(value, expected_value):
    assert mongo_fields.coerce_boolean(value) == expected_value


def test_coerce_boolean__raise_on_unexpected_value():
    with pytest.raises(ValueError) as error:
        mongo_fields.coerce_boolean("some")
    assert str(error.value) == "Unexpected string value."


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


class TestEmptyStringIsNoneMixin:
    """Special mixin to ignore empty strings **before** parent class processing."""

    class ParentClass:
        """MRO parent."""

        def __init__(self):
            self.data = True

        def process_formdata(self, valuelist):
            """Status changer"""
            assert valuelist != ""
            self.data = False

    class FakeClass(mongo_fields.EmptyStringIsNoneMixin, ParentClass):
        """Just MRO setter."""

        pass

    @pytest.mark.parametrize("value", ["", None, [], {}, (), "", ("",), [""]])
    def test__process_formdata__does_not_call_parent_method_if_value_is_empty(
        self, value
    ):
        obj = self.FakeClass()
        assert obj.data is True
        obj.process_formdata(value)
        assert obj.data is None

    @pytest.mark.parametrize("value", [[None], [1], (1,), (" ",), [" "]])
    def test__process_formdata__does_call_parent_method_if_value_is_not_empty(
        self, value
    ):
        obj = self.FakeClass()
        assert obj.data is True
        obj.process_formdata(value)
        assert obj.data is False


class TestMongoEmailField:
    def test_email_field_mro_not_changed(self):
        field_mro = list(mongo_fields.MongoEmailField.__mro__[:4])
        assert field_mro == [
            mongo_fields.MongoEmailField,
            mongo_fields.EmptyStringIsNoneMixin,
            wtf_fields.EmailField,
            wtf_fields.StringField,
        ]


class TestMongoHiddenField:
    def test_hidden_field_mro_not_changed(self):
        field_mro = list(mongo_fields.MongoHiddenField.__mro__[:4])
        assert field_mro == [
            mongo_fields.MongoHiddenField,
            mongo_fields.EmptyStringIsNoneMixin,
            wtf_fields.HiddenField,
            wtf_fields.StringField,
        ]


class TestMongoPasswordField:
    def test_password_field_mro_not_changed(self):
        field_mro = list(mongo_fields.MongoPasswordField.__mro__[:4])
        assert field_mro == [
            mongo_fields.MongoPasswordField,
            mongo_fields.EmptyStringIsNoneMixin,
            wtf_fields.PasswordField,
            wtf_fields.StringField,
        ]


class TestMongoSearchField:
    def test_search_field_mro_not_changed(self):
        field_mro = list(mongo_fields.MongoSearchField.__mro__[:4])
        assert field_mro == [
            mongo_fields.MongoSearchField,
            mongo_fields.EmptyStringIsNoneMixin,
            wtf_fields.SearchField,
            wtf_fields.StringField,
        ]


class TestMongoStringField:
    def test__parent__process_formdata__method_included_in_mro_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(wtf_fields.StringField, "process_formdata")
        mixin_init_spy = mocker.spy(
            mongo_fields.EmptyStringIsNoneMixin, "process_formdata"
        )

        class DocumentModel(db.Document):
            """Test DB model."""

            string_field = db.StringField()

        DocumentForm = DocumentModel.to_wtf_form()
        form = DocumentForm(formdata=MultiDict({"string_field": "1"}))
        assert form.validate()
        obj = form.save()
        mixin_init_spy.assert_called_once()
        base_init_spy.assert_called_once()
        assert obj.string_field == "1"

    def test_string_field_mro_not_changed(self):
        field_mro = list(mongo_fields.MongoStringField.__mro__[:3])
        assert field_mro == [
            mongo_fields.MongoStringField,
            mongo_fields.EmptyStringIsNoneMixin,
            wtf_fields.StringField,
        ]


class TestMongoTelField:
    def test_tel_field_mro_not_changed(self):
        field_mro = list(mongo_fields.MongoTelField.__mro__[:4])
        assert field_mro == [
            mongo_fields.MongoTelField,
            mongo_fields.EmptyStringIsNoneMixin,
            wtf_fields.TelField,
            wtf_fields.StringField,
        ]


class TestMongoTextAreaField:
    def test_text_area_field_mro_not_changed(self):
        field_mro = list(mongo_fields.MongoTextAreaField.__mro__[:4])
        assert field_mro == [
            mongo_fields.MongoTextAreaField,
            mongo_fields.EmptyStringIsNoneMixin,
            wtf_fields.TextAreaField,
            wtf_fields.StringField,
        ]


class TestMongoURLField:
    def test_url_field_mro_not_changed(self):
        field_mro = list(mongo_fields.MongoURLField.__mro__[:4])
        assert field_mro == [
            mongo_fields.MongoURLField,
            mongo_fields.EmptyStringIsNoneMixin,
            wtf_fields.URLField,
            wtf_fields.StringField,
        ]


class TestMongoFloatField:
    def test_ensure_widget_not_accidentally_replaced(self):
        field = mongo_fields.MongoFloatField
        assert isinstance(field.widget, wtf_widgets.NumberInput)
