"""Tests for db_fields overwrite and WTForms integration."""
import re
from enum import Enum
from unittest.mock import Mock

import pytest
from mongoengine import fields as base_fields
from pytest_mock import MockerFixture

from flask_mongoengine import db_fields, documents

try:
    from wtforms import fields as wtf_fields
    from wtforms import validators as wtf_validators_

    from flask_mongoengine.wtf import fields as mongo_fields

    wtforms_not_installed = False
except ImportError:
    wtf_validators_ = None
    wtf_fields = None
    mongo_fields = None
    wtforms_not_installed = True


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

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
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

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__to_wtf_form__logs_error(self, caplog, TempDocument):
        TempDocument.to_wtf_form()

        # Check error logging
        assert (
            "Field field_one ignored, field type does not have .to_wtf_field() method or "
            "method raised NotImplementedError."
        ) in caplog.messages


class TestWtfFieldMixin:
    # noinspection PyAbstractClass
    class WTFieldBaseMRO(db_fields.WtfFieldMixin, base_fields.BaseField):
        """Just an MRO setter for testing any BaseField child."""

        pass

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

    @pytest.mark.parametrize(
        "FieldClass",
        [
            db_fields.BinaryField,
            db_fields.CachedReferenceField,
            db_fields.DynamicField,
            db_fields.EmbeddedDocumentField,
            db_fields.EmbeddedDocumentListField,
            db_fields.EnumField,
            db_fields.FileField,
            db_fields.GenericEmbeddedDocumentField,
            db_fields.GenericLazyReferenceField,
            db_fields.GenericReferenceField,
            db_fields.GeoJsonBaseField,
            db_fields.GeoPointField,
            db_fields.ImageField,
            db_fields.LazyReferenceField,
            db_fields.LineStringField,
            db_fields.ListField,
            db_fields.LongField,
            db_fields.MapField,
            db_fields.MultiLineStringField,
            db_fields.MultiPointField,
            db_fields.MultiPolygonField,
            db_fields.ObjectIdField,
            db_fields.PointField,
            db_fields.PolygonField,
            db_fields.ReferenceField,
            db_fields.SequenceField,
            db_fields.SortedListField,
            db_fields.UUIDField,
        ],
    )
    def test__ensure_nested_field_class__to_wtf_field__method_disabled(
        self, FieldClass, mocker: MockerFixture
    ):
        """
        It is expected, that amount of such classes will be decreased in the future.

        __init__ method mocked to limit test scope.
        """
        mocker.patch.object(db_fields.WtfFieldMixin, "__init__", return_value=None)
        field = FieldClass()
        with pytest.raises(NotImplementedError):
            field.to_wtf_field(model=None, field_kwargs=None)

    def test__init__method__warning__if_deprecated__validators__set(self, recwarn):
        db_fields.WtfFieldMixin(validators=[])
        assert str(recwarn.list[0].message) == (
            "Passing 'validators' keyword argument to field definition is "
            "deprecated and will be removed in version 3.0.0. "
            "Please rename 'validators' to 'wtf_validators'. "
            "If both values set, 'wtf_validators' is used."
        )

    def test__init__method__warning__if_deprecated__filters__set(self, recwarn):
        db_fields.WtfFieldMixin(filters=[])
        assert str(recwarn.list[0].message) == (
            "Passing 'filters' keyword argument to field definition is "
            "deprecated and will be removed in version 3.0.0. "
            "Please rename 'filters' to 'wtf_filters'. "
            "If both values set, 'wtf_filters' is used."
        )

    def test__wtf_field_class__return__DEFAULT_WTF_FIELD__value_if_no_init_options_set(
        self,
    ):
        field = db_fields.WtfFieldMixin()
        field.DEFAULT_WTF_FIELD = "fake"
        assert field.wtf_field_class == "fake"

    def test__wtf_field_class__return__DEFAULT_WTF_CHOICES_FIELD_value_if_choices_options_set(
        self,
    ):
        field = db_fields.StringField(choices=(1, 2, 3))
        field.DEFAULT_WTF_CHOICES_FIELD = "fake"
        assert issubclass(field.__class__, db_fields.WtfFieldMixin)
        assert field.wtf_field_class == "fake"

    def test__wtf_field_class__return__user_provided_value__if_set(self):
        field = db_fields.WtfFieldMixin(wtf_field_class=str)

        assert issubclass(field.wtf_field_class, str)

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    @pytest.mark.parametrize(
        ["user_dict", "expected_result"],
        [
            ({"fake": "replaced"}, {"fake": "replaced"}),
            ({"added_arg": "added"}, {"fake": "dict", "added_arg": "added"}),
            (None, {"fake": "dict"}),
        ],
    )
    def test__wtf_field_options__overwrite_generated_options_with_user_provided(
        self, mocker: MockerFixture, user_dict, expected_result
    ):
        mocker.patch.object(
            db_fields.WtfFieldMixin,
            "wtf_generated_options",
            new_callable=lambda: {"fake": "dict"},
        )

        field = db_fields.WtfFieldMixin(wtf_options=user_dict)
        assert field.wtf_field_options == expected_result

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__wtf_generated_options__correctly_retrieve_label_from_parent_class(self):
        """Test based on base class for all fields."""
        default_call = self.WTFieldBaseMRO()
        default_call.name = "set not by init"  # set by metaclass for documents
        with_option_call = self.WTFieldBaseMRO(verbose_name="fake")

        assert default_call.wtf_generated_options["label"] == "set not by init"
        assert with_option_call.wtf_generated_options["label"] == "fake"

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__wtf_generated_options__correctly_retrieve_description_from_parent_class(
        self,
    ):
        default_call = self.WTFieldBaseMRO()
        with_option_call = self.WTFieldBaseMRO(help_text="fake")

        assert default_call.wtf_generated_options["description"] == ""
        assert with_option_call.wtf_generated_options["description"] == "fake"

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__wtf_generated_options__correctly_retrieve_default_from_parent_class(self):
        default_call = self.WTFieldBaseMRO()
        with_option_call = self.WTFieldBaseMRO(default="fake")

        assert default_call.wtf_generated_options["default"] is None
        assert with_option_call.wtf_generated_options["default"] == "fake"

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__wtf_generated_options__correctly_retrieve_validators_from_parent_class__and__add_optional_validator__if_field_not_required(
        self,
    ):
        default_call = self.WTFieldBaseMRO()
        with_option_call = self.WTFieldBaseMRO(wtf_validators=[str, int])

        assert isinstance(
            default_call.wtf_generated_options["validators"][0],
            wtf_validators_.Optional,
        )
        assert len(with_option_call.wtf_generated_options["validators"]) == 3
        assert isinstance(
            with_option_call.wtf_generated_options["validators"][-1],
            wtf_validators_.Optional,
        )

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__wtf_generated_options__correctly_retrieve_validators_from_parent_class__and__add_required__if_field_required(
        self,
    ):
        default_call = self.WTFieldBaseMRO(required=True)
        with_option_call = self.WTFieldBaseMRO(required=True, wtf_validators=[str, int])

        assert isinstance(
            default_call.wtf_generated_options["validators"][0],
            wtf_validators_.InputRequired,
        )
        assert len(with_option_call.wtf_generated_options["validators"]) == 3
        assert isinstance(
            with_option_call.wtf_generated_options["validators"][-1],
            wtf_validators_.InputRequired,
        )

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__wtf_generated_options__correctly_retrieve_filters_from_parent_class(self):
        default_call = self.WTFieldBaseMRO()
        with_option_call = self.WTFieldBaseMRO(wtf_filters=[str, list])

        assert default_call.wtf_generated_options["filters"] == []
        assert with_option_call.wtf_generated_options["filters"] == [str, list]

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__wtf_generated_options__correctly_handle_choices_settings(self):
        default_call = self.WTFieldBaseMRO(choices=[1, 2])
        with_option_call = self.WTFieldBaseMRO(choices=[1, 2], wtf_choices_coerce=list)

        assert default_call.wtf_generated_options["choices"] == [1, 2]
        assert default_call.wtf_generated_options["coerce"] is str
        assert with_option_call.wtf_generated_options["choices"] == [1, 2]
        assert with_option_call.wtf_generated_options["coerce"] is list

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__to_wtf_field__does_not_modify_anything_if_options_not_provided(self):
        # Setting base validators to exclude patching of .wtf_generated_options()
        field = self.WTFieldBaseMRO(wtf_options={"validators": ["ignore"]})
        field.DEFAULT_WTF_FIELD = Mock()
        field_options = field.wtf_field_options

        field.to_wtf_field()

        field.DEFAULT_WTF_FIELD.assert_called_with(**field_options)

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__to_wtf_field__update_field_class_if_related_option_provided(self):
        # Setting base validators to exclude patching of .wtf_generated_options()
        will_be_called = Mock()
        will_not_be_called = Mock()
        field = self.WTFieldBaseMRO(wtf_options={"validators": ["ignore"]})
        field.DEFAULT_WTF_FIELD = will_not_be_called
        field_options = field.wtf_field_options
        field.to_wtf_field(field_kwargs={"wtf_field_class": will_be_called})

        will_not_be_called.assert_not_called()
        will_be_called.assert_called_with(**field_options)

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__to_wtf_field__update_field_kwargs_if_related_option_provided(self):
        # Setting base validators to exclude patching of .wtf_generated_options()
        will_be_called = Mock()
        field = self.WTFieldBaseMRO(wtf_options={"validators": ["ignore"]})
        field_options = field.wtf_field_options
        field_options.update({"update": "this"})
        field.to_wtf_field(
            field_kwargs={"wtf_field_class": will_be_called, "update": "this"}
        )

        will_be_called.assert_called_with(**field_options)


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

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__form_field_class__is_email_field__even_if_size_given__and_validators_set(
        self, db
    ):
        field = db.EmailField(max_length=3, min_length=1)

        assert field.wtf_field_class is mongo_fields.MongoEmailField
        validator = [
            val
            for val in field.wtf_field_options["validators"]
            if val.__class__ is wtf_validators_.Length
        ][0]
        assert validator is not None
        assert validator.min == 1
        assert validator.max == 3


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


@pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
@pytest.mark.parametrize(
    "StringClass",
    [
        db_fields.StringField,
        db_fields.URLField,
        db_fields.EmailField,
    ],
)
class TestStringFieldCommons:
    """
    Ensure all string based classes call :func:`~._setup_strings_common_validators`
    and get expected results.
    """

    @pytest.mark.parametrize(
        ["min_", "max_", "validator_min", "validator_max"],
        [
            [None, 3, -1, 3],
            [3, None, 3, -1],
            [3, 5, 3, 5],
        ],
    )
    def test__init__method__set_length_validator__if_size_given(
        self, StringClass, min_, max_, validator_min, validator_max
    ):
        field = StringClass(min_length=min_, max_length=max_)
        validator = [
            val
            for val in field.wtf_field_options["validators"]
            if val.__class__ is wtf_validators_.Length
        ][0]
        assert validator is not None
        assert validator.min == validator_min
        assert validator.max == validator_max

    def test__init__method__set_regex_validator__if_option(self, StringClass):
        field = StringClass(regex="something")
        validator = [
            val
            for val in field.wtf_field_options["validators"]
            if val.__class__ is wtf_validators_.Regexp
        ][-1]
        assert validator is not None
        assert validator.regex == re.compile("something")


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

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__init__method_report_warning__if_password_keyword_setting_set(
        self, recwarn
    ):
        field = db_fields.StringField(password=True)
        assert str(recwarn.list[0].message) == (
            "Passing 'password' keyword argument to field definition is "
            "deprecated and will be removed in version 3.0.0. "
            "Please use 'wtf_field_class' parameter to specify correct field "
            "class. If both values set, 'wtf_field_class' is used."
        )
        assert issubclass(field.wtf_field_class, wtf_fields.PasswordField)

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__init__method_report_warning__if_textarea_keyword_setting_set(
        self, recwarn
    ):
        field = db_fields.StringField(textarea=True)
        assert str(recwarn.list[0].message) == (
            "Passing 'textarea' keyword argument to field definition is "
            "deprecated and will be removed in version 3.0.0. "
            "Please use 'wtf_field_class' parameter to specify correct field "
            "class. If both values set, 'wtf_field_class' is used."
        )
        assert issubclass(field.wtf_field_class, wtf_fields.TextAreaField)

    def test__init__method_raise_error__if_password_and_keyword_setting_both_set(self):
        with pytest.raises(ValueError) as error:
            db_fields.StringField(textarea=True, password=True)

        assert str(error.value) == "Password field cannot use TextAreaField class."

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__init__method__set_textarea__in__wtf_field_class__even_if_size_given(self):
        field = db_fields.StringField(textarea=True, min_length=3)
        assert field.wtf_field_class is mongo_fields.MongoTextAreaField

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    @pytest.mark.parametrize(
        ["min_", "max_"],
        [
            [None, 3],
            [3, None],
            [3, 5],
        ],
    )
    def test__init__method__set_string_field_class__if_size_given(self, min_, max_):
        field = db_fields.StringField(min_length=min_, max_length=max_)
        validator = [
            val
            for val in field.wtf_field_options["validators"]
            if val.__class__ is wtf_validators_.Length
        ]
        assert field.wtf_field_class is mongo_fields.MongoStringField
        assert validator is not None


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

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__form_field_class__is_url_field__even_if_size_given__and_validators_set(
        self, db
    ):
        field = db.URLField(max_length=3, min_length=1)

        assert field.wtf_field_class is mongo_fields.MongoURLField
        validator = [
            val
            for val in field.wtf_field_options["validators"]
            if val.__class__ is wtf_validators_.Length
        ][0]
        assert validator is not None
        assert validator.min == 1
        assert validator.max == 3


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


@pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
@pytest.mark.parametrize(
    "NumberClass",
    [
        db_fields.FloatField,
        db_fields.IntField,
        db_fields.DecimalField,
    ],
)
class TestNumberFieldCommons:
    @pytest.mark.parametrize(
        ["min_", "max_", "validator_min", "validator_max"],
        [
            [None, 3, None, 3],
            [None, -3, None, -3],
            [3, None, 3, None],
            [-3, None, -3, None],
            [-1, -3, -1, -3],
            [3, 5, 3, 5],
        ],
    )
    def test__init__method__set_number_range_validator__if_range_given(
        self, NumberClass, min_, max_, validator_min, validator_max
    ):
        field = NumberClass(min_value=min_, max_value=max_)
        validator = [
            val
            for val in field.wtf_field_options["validators"]
            if val.__class__ is wtf_validators_.NumberRange
        ][0]
        assert validator is not None
        assert validator.min == validator_min
        assert validator.max == validator_max
