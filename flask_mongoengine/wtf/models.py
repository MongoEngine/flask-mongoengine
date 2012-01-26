from wtforms.form import Form


def update_path(self, **kwargs):

    def _get_list(f):
        def _wrapper(o, n):
            if o and not isinstance(o, (list, tuple)):
                raise Exception('must be list')
            return f(o, n) or o
        return _wrapper

    transforms = {
        'set': lambda o, n: n,
        'unset': lambda o, n: None,
        'inc': lambda o, n: o + n,
        'dec': lambda o, n: o - n,
        'push': _get_list(lambda o, n: not o and [n] or o.appned(n)),
        'push_all': _get_list(lambda o, n: not o and n or o.extend(n)),
        'pull': _get_list(lambda o, n: n in o and o.remove(n)),
        'pull_all': _get_list(lambda o, n: reduce(lambda x, y: y in o and o.remove(y), n, False)),
    }

    self.commit = kwargs.pop('commit', True)

    for key, value in kwargs.iteritems():
        parts = key.split('__')
        old = getattr(self, parts[1])
        value = transforms[parts[0]](old, value)
        setattr(self, parts[1], value)
    if not self.commit:
        return
    return self.__class__.objects(id=self.id).update_one(**kwargs)

# Path instance
from mongoengine.document import Document
Document.update = update_path


class ModelForm(Form):
    def __init__(self, *args, **kwargs):
        #self.model_class = kwargs.pop('model_class', None)
        self.instance = kwargs['obj'] = kwargs.pop('instance', None) or \
                                        kwargs.get('obj', None)
        super(ModelForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        if self.instance:
            update = {}
            for name, field in self._fields.iteritems():
                try:
                    if getattr(self.instance, name) != field.data:
                        update['set__' + name] = field.data
                except AttributeError:
                    raise Exception('Model %s has not attr %s but form %s has' \
                                    % (type(self.instance),
                                      name,
                                      type(self)))
            update['commit'] = commit
            self.instance.update(**update)
        else:
            self.instance = self.model_class(**self.data)
            if commit:
                self.instance.save()
        return self.instance
