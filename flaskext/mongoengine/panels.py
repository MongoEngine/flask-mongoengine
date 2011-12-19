from flask import current_app

from flaskext.debugtoolbar.panels import DebugPanel
from jinja2 import PackageLoader, ChoiceLoader
import operation_tracker

_ = lambda x: x


class MongoenginePanel(DebugPanel):
    """ Panel deprecated in favor of MongoDebugPanel """

    name = 'Mongoengine'
    has_content = True

    def process_response(self, request, response):
        pass

    def nav_title(self):
        return _('Mongoengine')

    def title(self):
        return _('Mongoengine Usage')

    def url(self):
        return ''

    def content(self):
        return '<h2>Panel deprecated in favor of MongoDebugPanel'


class MongoDebugPanel(DebugPanel):
    """Panel that shows information about MongoDB operations (including stack)

    Adapted from https://github.com/hmarr/django-debug-toolbar-mongo
    """
    name = 'MongoDB'
    has_content = True

    def __init__(self, *args, **kwargs):
        """
        We need to patch jinja_env loader to include flaskext.mongoengine
        templates folder.
        """
        super(MongoDebugPanel, self).__init__(*args, **kwargs)
        self.jinja_env.loader = ChoiceLoader([self.jinja_env.loader,
                          PackageLoader('flaskext.mongoengine', 'templates')])
        operation_tracker.install_tracker()

    def process_request(self, request):
        operation_tracker.reset()

    def nav_title(self):
        return 'MongoDB'

    def nav_subtitle(self):
        num_queries = len(operation_tracker.queries)
        attrs = ['queries', 'inserts', 'updates', 'removes']
        total_time = sum(sum(o['time'] for o in getattr(operation_tracker, a))
                         for a in attrs)
        return '{0} operations in {1:.2f}ms'.format(num_queries, total_time)

    def title(self):
        return 'MongoDB Operations'

    def url(self):
        return ''

    def content(self):
        context = self.context.copy()
        context['queries'] = operation_tracker.queries
        context['inserts'] = operation_tracker.inserts
        context['updates'] = operation_tracker.updates
        context['removes'] = operation_tracker.removes
        context['slow_query_limit'] = current_app.config.get('MONGO_DEBUG_PANEL_SLOW_QUERY_LIMIT', 100)
        return self.render('panels/mongo-panel.html', context)
