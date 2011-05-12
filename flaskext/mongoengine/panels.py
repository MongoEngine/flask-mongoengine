import re

import pymongo

from flaskext.debugtoolbar.panels import DebugPanel
from jinja2 import PackageLoader, ChoiceLoader
from mongoengine.connection import _get_db

_ = lambda x: x


class MongoenginePanel(DebugPanel):
    """
    Panel that displays the number of mongodb queries using mongoengine.

     * nscanned_vs_nreturned_ratio: Ratio to determine if a query needs index.
     * nscanned_update_limit: Limit to determine if a update query needs index.
     * slow_query_limit: Limit (ms) to determine if a query is slow.

    """

    name = 'Mongoengine'
    has_content = True
    nscanned_vs_nreturned_ratio = 1000
    nscanned_update_limit = 1000
    slow_query_limit = 100

    def __init__(self, *args, **kwargs):
        """
        We need to patch jinja_env loader to include flaskext.mongoengine
        templates folder.
        """
        super(MongoenginePanel, self).__init__(*args, **kwargs)
        self.jinja_env.loader = ChoiceLoader([self.jinja_env.loader,
                          PackageLoader('flaskext.mongoengine', 'templates')])
        self.db = _get_db()

    def process_request(self, request):
        """
        This panel use the mongodb Database Profiler [1]

        On every request we deactivate, get the biggest ts and reactivate the
        profiler.

        [1] http://www.mongodb.org/display/DOCS/Database+Profiler
        """
        self.db.set_profiling_level(0)
        self.start_ts = self.db.system.profile.find()\
                                              .sort("ts", pymongo.DESCENDING)\
                                              .limit(1)[0].get('ts')
        self.db.set_profiling_level(2)

    def _get_property(self, key, query):
        try:
            return float(re.search(r'%s\:(\d+)' % key, query).group(1))
        except:
            return None

    def _should_optimize(self, query):
        """
        Try to determine if there are any applicable obvious optimizations
        http://www.mongodb.org/display/DOCS/Database+Profiler

        index: If nscanned is much higher than nreturned, the database is
               scanning many objects to find the target objects. Consider
               creating an index to improve this.

        select members: (reslen) A large number of bytes returned (hundreds
               of kilobytes or more) causes slow performance. Consider passing
               find() a second parameter of the member names you require.
        """
        optimizations = []

        if query['operation_type'] == 'query':
            nscanned = self._get_property('nscanned', query['org_info'])
            nreturned = self._get_property('nreturned', query['org_info'])
            if (nreturned and nscanned) and \
               (nscanned > nreturned * self.nscanned_vs_nreturned_ratio):
                optimizations.append("index")

            reslen = self._get_property('reslen', query['org_info'])
            if reslen > 100 * 1024:
                optimizations.append("select members")

        elif query['operation_type'] == 'update':
            nscanned = self._get_property('nscanned', query['org_info'])

            if nscanned and nscanned > self.nscanned_update_limit:
                optimizations.append("index")

        if query['millis'] > self.slow_query_limit:
            optimizations.append("slow")

        return optimizations

    def _process_query(self, query):
        """
        Split the query to recover all interesting information.
        """
        query_search_pattern = r'\nquery: (\{.*\})  nreturned'
        query_search_remove_pattern = r'(.*)(\nquery: \{.*\} )( nreturned.*)'

        command_search_pattern = r'command: (\{.*\}) reslen'
        command_search_remove_pattern = r'(.*)(command: \{.*\})( reslen.*)'

        out = {}
        out['millis'] = query.get('millis', 0)
        out['ts'] = query.get('ts')

        out['org_info'] = query.get('info')

        info = query.get('info').split(' ')
        out['operation_type'] = info[0]
        out['collection'] = info[1]

        info = ' '.join(info[2:])
        mongo_query = re.search(query_search_pattern, info)
        mongo_command = re.search(command_search_pattern, info)

        if mongo_query:
            out['query'] = mongo_query.group(1)
            info = re.sub(query_search_remove_pattern, r'\1\3', info)

        elif mongo_command:
            out['query'] = mongo_command.group(1)
            info = re.sub(command_search_remove_pattern, r'\1\3', info)
        else:
            out['query'] = ""

        out['extra'] = info
        out['optimizations'] = ', '.join(self._should_optimize(out))

        return out

    def process_response(self, request, response):
        """
        Get queries from system.profile with ts > self.start_ts
        """
        query = {'ts': {'$gt': self.start_ts}}
        self.queries = self.db.system.profile.find(query, timeout=False)
        self.queries = [self._process_query(q) for q in self.queries]
        self.queries_count = len(self.queries)
        self.total_time = sum([q.get('millis') for q in self.queries])

    def nav_title(self):
        return _('Mongoengine')

    def nav_subtitle(self):
        return "%s queries in %sms" % (self.queries_count, self.total_time)

    def title(self):
        return _('Mongoengine Usage')

    def url(self):
        return ''

    def content(self):

        context = self.context.copy()
        context.update({
            'queries': self.queries,
        })

        return self.render('panels/mongoengine.html', context)
