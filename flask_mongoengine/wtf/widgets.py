"""Custom widgets for Mongo fields."""
from markupsafe import Markup, escape
from mongoengine.fields import GridFSProxy
from wtforms.widgets import html_params


class MongoFileInput(object):
    """Renders a file input field with delete option."""

    template = """
        <div>
        <i class="icon-file"></i>%(name)s %(size)dk (%(content_type)s)
        <input type="checkbox" name="%(marker)s">Delete</input>
        </div>
        """

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        placeholder = ""
        if field.data and isinstance(field.data, GridFSProxy):
            data = field.data
            placeholder = self.template % {
                "name": escape(data.name),
                "content_type": escape(data.content_type),
                "size": data.length // 1024,
                "marker": f"_{field.name}_delete",
            }

        return Markup(
            (
                "%s<input %s>"
                % (placeholder, html_params(name=field.name, type="file", **kwargs))
            )
        )
