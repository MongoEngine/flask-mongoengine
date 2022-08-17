"""Custom widgets for Mongo fields."""
from markupsafe import Markup, escape
from mongoengine.fields import GridFSProxy, ImageGridFsProxy
from wtforms.widgets.core import FileInput


class MongoFileInput(FileInput):
    """Renders a file input field with delete option."""

    template = """
        <div>
        <i class="icon-file"></i>%(name)s %(size)dk (%(content_type)s)
        <input type="checkbox" name="%(marker)s">Delete</input>
        </div>
        """

    def _is_supported_file(self, field) -> bool:
        """Checks type of file input."""
        return field.data and isinstance(field.data, GridFSProxy)

    def __call__(self, field, **kwargs) -> Markup:
        placeholder = ""

        if self._is_supported_file(field):
            placeholder = self.template % {
                "name": escape(field.data.name),
                "content_type": escape(field.data.content_type),
                "size": field.data.length // 1024,
                "marker": f"_{field.name}_delete",
            }

        return Markup(placeholder) + super().__call__(field, **kwargs)


class MongoImageInput(MongoFileInput):
    """Renders an image input field with delete option."""

    def _is_supported_file(self, field) -> bool:
        """Checks type of file input."""
        return field.data and isinstance(field.data, ImageGridFsProxy)
