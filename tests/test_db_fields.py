"""Tests for db_fields overwrite and WTForms integration."""
from enum import Enum

import pytest
from mongoengine import fields as base_fields
from pytest_mock import MockerFixture

from flask_mongoengine import db_fields, documents


@pytest.fixture
def local_app(app):
    """Helper fixture to minimize code indentation."""
    with app.test_request_context("/"):
        yield app


class TestWtfFormMixin:
    @pytest.fixture(
        params=[
            documents.Document,
            documents.DynamicDocument,
            documents.DynamicEmbeddedDocument,
            documents.EmbeddedDocument,
        ]
    )
    def TempDocument(self, request):
        """Cool fixture"""

        class Model(request.param):
            """
            Temp document model for most of the tests.

            field_one by design cannot be converted to FormField.
            """

            field_one = base_fields.StringField()
            field_two = db_fields.StringField()
            field_three = db_fields.StringField()
            field_four = db_fields.StringField()
            field_five = db_fields.StringField()

        return Model

    def test__get_fields_names__is_called_by_to_wtf_form_call(
        self, TempDocument, mocker: MockerFixture
    ):
        get_fields_names_spy = mocker.patch.object(
            documents.WtfFormMixin, "_get_fields_names", autospec=True
        )
        TempDocument.to_wtf_form()
        get_fields_names_spy.assert_called_once()

    def test__get_fields_names__hold_correct_fields_ordering_for_only(
        self, TempDocument
    ):

        field_names = TempDocument._get_fields_names(
            only=["field_five", "field_one"], exclude=None
        )
        assert field_names == ["field_five", "field_one"]

    def test__get_fields_names__hold_correct_fields_ordering_for_exclude(
        self, TempDocument
    ):
        field_names = TempDocument._get_fields_names(
            only=None, exclude=["id", "field_five", "field_one"]
        )
        assert field_names == ["field_two", "field_three", "field_four"]

    def test__to_wtf_form__is_called_by_mixin_child_model(
        self, TempDocument, caplog, mocker: MockerFixture
    ):
        to_wtf_spy = mocker.patch.object(
            documents.WtfFormMixin, "to_wtf_form", autospec=True
        )
        TempDocument.to_wtf_form()
        to_wtf_spy.assert_called_once()

    def test__to_wtf_form__logs_error(self, caplog, TempDocument):
        TempDocument.to_wtf_form()

        # Check error logging
        assert (
            "Field field_one ignored, field type does not have .to_wtf_field() method or "
            "method raised NotImplementedError."
        ) in caplog.messages


class TestWtfFieldMixin:
    def test__init__set_additional_instance_arguments(self, db, mocker: MockerFixture):
        checker_spy = mocker.spy(db_fields.WtfFieldMixin, "_ensure_callable_or_list")

        string = db.StringField(validators=[1, 2], filters=[1, 2])
        assert string.wtf_validators == [1, 2]
        assert string.wtf_filters == [1, 2]
        checker_spy.assert_called()
        assert checker_spy.call_count == 2

    def test__ensure_callable_or_list__return_none_if_argument_is_none(self):
        assert (
            db_fields.WtfFieldMixin._ensure_callable_or_list(argument=None, msg_flag="")
            == []
        )

    def test__ensure_callable_or_list__return_callable_argument_as_list(self):
        assert db_fields.WtfFieldMixin._ensure_callable_or_list(
            argument=dict, msg_flag=""
        ) == [dict]

    def test__ensure_callable_or_list__return_list_argument_as_list(self):
        assert db_fields.WtfFieldMixin._ensure_callable_or_list(
            argument=[1, 2], msg_flag=""
        ) == [1, 2]

    def test__ensure_callable_or_list__raise_error_if_argument_not_callable_and_not_list(
        self,
    ):
        with pytest.raises(TypeError) as error:
            db_fields.WtfFieldMixin._ensure_callable_or_list(
                argument=1, msg_flag="field"
            )
        assert str(error.value) == "Argument 'field' must be a list value"


class TestBinaryField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.BinaryField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.BinaryField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestBooleanField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.BooleanField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.BooleanField()
        base_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestCachedReferenceField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.CachedReferenceField`"""

    def test__parent__init__method_included_in_init_chain(self, db, todo, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.CachedReferenceField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.CachedReferenceField(document_type=todo)
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestComplexDateTimeField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.ComplexDateTimeField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.ComplexDateTimeField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.ComplexDateTimeField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestDateField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.DateField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.DateField()
        base_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestDateTimeField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.DateTimeField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.DateTimeField()
        base_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestDecimalField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.DecimalField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.DecimalField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.DecimalField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestDictField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.DictField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.DictField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.DictField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestDynamicField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.DynamicField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.DynamicField()
        base_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestEmailField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.EmailField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.EmailField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.EmailField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestEmbeddedDocumentField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.EmbeddedDocumentField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""

        class Todo(db.EmbeddedDocument):
            """Special EmbeddedDocument class to match test condition."""

            string = db.StringField()

        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.EmbeddedDocumentField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.EmbeddedDocumentField(document_type=Todo)
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestEmbeddedDocumentListField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.EmbeddedDocumentListField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""

        class Todo(db.EmbeddedDocument):
            """Special EmbeddedDocument class to match test condition."""

            string = db.StringField()

        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.EmbeddedDocumentListField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.EmbeddedDocumentListField(document_type=Todo)
        base_init_spy.assert_called()
        assert base_init_spy.call_count == 2
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestEnumField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.EnumField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""

        class Status(Enum):
            """Special Enum class to match test condition."""

            NEW = "new"
            ONGOING = "ongoing"
            DONE = "done"

        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.EnumField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.EnumField(enum=Status)
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestFileField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.FileField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.FileField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.FileField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestFloatField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.FloatField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.FloatField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.FloatField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestGenericEmbeddedDocumentField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.GenericEmbeddedDocumentField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.GenericEmbeddedDocumentField()
        base_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestGenericLazyReferenceField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.GenericLazyReferenceField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.GenericLazyReferenceField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.GenericLazyReferenceField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestGenericReferenceField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.GenericReferenceField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.GenericReferenceField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.GenericReferenceField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestGeoJsonBaseField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.GeoJsonBaseField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.GeoJsonBaseField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.GeoJsonBaseField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestGeoPointField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.GeoPointField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.GeoPointField()
        base_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestImageField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.ImageField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.ImageField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.ImageField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestIntField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.IntField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.IntField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.IntField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestLazyReferenceField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.LazyReferenceField`"""

    def test__parent__init__method_included_in_init_chain(self, db, todo, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.LazyReferenceField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.LazyReferenceField(document_type=todo)
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestLineStringField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.LineStringField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.LineStringField()
        base_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestListField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.ListField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.ListField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.ListField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestLongField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.LongField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.LongField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.LongField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestMapField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.MapField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        temp_field = db.StringField()
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.MapField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.MapField(field=temp_field)
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestMultiLineStringField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.MultiLineStringField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.MultiLineStringField()
        base_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestMultiPointField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.MultiPointField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.MultiPointField()
        base_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestMultiPolygonField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.MultiPolygonField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.MultiPolygonField()
        base_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestObjectIdField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.ObjectIdField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.ObjectIdField()
        base_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestPointField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.PointField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.PointField()
        base_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestPolygonField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.PolygonField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.PolygonField()
        base_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestReferenceField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.ReferenceField`"""

    def test__parent__init__method_included_in_init_chain(self, db, todo, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.ReferenceField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.ReferenceField(document_type=todo)
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestSequenceField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.SequenceField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.SequenceField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.SequenceField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestSortedListField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.SortedListField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        temp_field = db.StringField()
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.SortedListField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.SortedListField(field=temp_field)
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestStringField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.StringField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.StringField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.StringField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestURLField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.URLField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.URLField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.URLField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()


class TestUUIDField:
    """Custom test set for :class:`~flask_mongoengine.wtf.db_fields.UUIDField`"""

    def test__parent__init__method_included_in_init_chain(self, db, mocker):
        """Test to protect from accidental incorrect __init__ method overwrite."""
        base_init_spy = mocker.spy(base_fields.BaseField, "__init__")
        field_init_spy = mocker.spy(base_fields.UUIDField, "__init__")
        mixin_init_spy = mocker.spy(db_fields.WtfFieldMixin, "__init__")
        db.UUIDField()
        base_init_spy.assert_called_once()
        field_init_spy.assert_called_once()
        mixin_init_spy.assert_called_once()
