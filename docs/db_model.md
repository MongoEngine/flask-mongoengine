# Database model and fields definition

```{important}
Flask-Mongoengine does not adjust database level behaviour of [mongoengine] fields
definition, except [keyword only definition] requirement. Everything other on
database level match [mongoengine] project. All parent methods, arguments (as
keyword arguments) and keyword arguments are supported.

If you are not intend to use WTForms integration, you are free to use fields classes
from parent [mongoengine] project; this should not break anything.
```

## Supported fields

Flask-Mongoengine support all **database** fields definition. Even if there will be some
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

Database model definition rules and Flask-WTF/WTForms [integration] was seriously
updated in version **2.0.0**. Unfortunately, these changes implemented without any
deprecation stages.

Before version **2.0.0** Flask-Mongoengine integration allowed to pass fields
parameters as arguments. To exclude any side effects or keyword parameters
duplication/conflicts, since version **2.0.0** all fields require keyword
only setup.

Such approach removes number of issues and questions, when users frequently used
Flask-WTF/WTForms definition rules by mistake, or just missed that some arguments
was passed to keyword places silently creating unexpected side effects. You can
check issue [#379] as example of one of such cases.

[mongoengine]: https://docs.mongoengine.org/
[#379]: https://github.com/MongoEngine/flask-mongoengine/issues/379
[integration]: forms
[keyword only definition]: #keyword-only-definition
