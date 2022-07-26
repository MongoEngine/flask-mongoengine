"""Testing independency from WTForms."""
import pytest

try:
    import wtforms

    wtforms_not_installed = False
except ImportError:
    wtforms = None
    wtforms_not_installed = True


class TestImportProtection:
    def test__when_wtforms_available__import_use_its_data(self):
        from flask_mongoengine import db_fields

        assert db_fields is not None

    def test__core_class_imported_without_error(self):
        from flask_mongoengine import MongoEngine

        db = MongoEngine()
        assert db is not None

    @pytest.mark.skipif(condition=wtforms_not_installed, reason="No WTF CI/CD chain")
    def test__wtf_required_decorator__when_wtf_installed(self):
        from flask_mongoengine.decorators import wtf_required

        @wtf_required
        def foo(a, b=None):
            """Temp function."""
            return a + b

        assert foo(1, 1) == 2

    def test__wtf_required_decorator__when_wtf_not_installed(self, caplog, monkeypatch):
        monkeypatch.setattr("flask_mongoengine.decorators.wtf_installed", False)
        from flask_mongoengine.decorators import wtf_required

        @wtf_required
        def foo(a, b=None):
            """Temp function."""
            return a + b

        x = foo(1, 1)
        assert x is None
        assert caplog.messages[0] == "WTForms not installed. Function 'foo' aborted."
