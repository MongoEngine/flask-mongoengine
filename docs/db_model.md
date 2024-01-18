# Database model and fields definition

```{important}
Flask-Mongoengine does not adjust database level behaviour of [mongoengine] fields
definition, except [keyword only definition] requirement. Everything other on
database level match [mongoengine] project. All parent methods, arguments (as
keyword arguments) and keyword arguments are supported.
```

## Supported fields

Flask-Mongoengine support all **database** fields definition. Even if there will be some
new field type created in parent [mongoengine] project, we will silently bypass
field definition to it, if we do not declare rules on our side.

```{note}
Version **2.0.0** Flask-Mongoengine update support [mongoengine] fields, based on
version **mongoengine==0.21**. Any new fields bypassed without modification.
```
