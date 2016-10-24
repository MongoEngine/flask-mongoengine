from flask_wtf import FlaskForm


class ModelForm(FlaskForm):
    """A WTForms mongoengine model form"""

    def __init__(self, formdata=None, obj=None, **kwargs):
        self.instance = (kwargs.pop('instance', None) or obj)
        if self.instance and not formdata:
            obj = self.instance
        self.formdata = formdata
        super(ModelForm, self).__init__(formdata, obj, **kwargs)

    def save(self, commit=True, **kwargs):
        if self.instance:
            self.populate_obj(self.instance)
        else:
            self.instance = self.model_class(**self.data)

        if commit:
            self.instance.save(**kwargs)
        return self.instance
