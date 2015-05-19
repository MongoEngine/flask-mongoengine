from mongoengine.base import BaseField

__all__ = ('WtfBaseField')

class WtfBaseField(BaseField):
    """
    Extension wrapper class for mongoengine BaseField.

    This enables flask-mongoengine  wtf to extend the
    number of field parameters, and settings on behalf
    of document model form generator for WTForm.

    """

    def __init__(self, validators=None, **kwargs):
        BaseField.__init__(self, **kwargs)

        # Ensure we have a list of validators
        if validators is not None:
            if callable(validators):
                validators = [validators]
            else:
                msg = "Argument 'validators' must be a list value"
                if not isinstance(validators, list):
                    raise TypeError(msg)
        self.validators = validators