import datetime
import sys
import uuid

from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict

__all__ = ("MongoEngineSession", "MongoEngineSessionInterface")

if sys.version_info >= (3, 0):
    basestring = str


class MongoEngineSession(CallbackDict, SessionMixin):

    def __init__(self, initial=None, sid=None):
        def on_update(self):
            self.modified = True
        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.modified = False


class MongoEngineSessionInterface(SessionInterface):
    """SessionInterface for mongoengine"""

    def __init__(self, db, collection='session'):
        """
        The MongoSessionInterface

        :param db: The app's db eg: MongoEngine()
        :param collection: The session collection name defaults to "session"
        """

        if not isinstance(collection, basestring):
            raise ValueError('collection argument should be string or unicode')

        class DBSession(db.Document):
            sid = db.StringField(primary_key=True)
            data = db.DictField()
            expiration = db.DateTimeField()
            meta = {
                'allow_inheritance': False,
                'collection': collection,
                'indexes': [{'fields': ['expiration'],
                             'expireAfterSeconds': 60 * 60 * 24 * 7 * 31}]
            }

        self.cls = DBSession

    def get_expiration_time(self, app, session):
        if session.permanent:
            return app.permanent_session_lifetime
        return datetime.timedelta(days=1)

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if sid:
            stored_session = self.cls.objects(sid=sid).first()
            if stored_session and stored_session.expiration > datetime.datetime.utcnow():
                return MongoEngineSession(initial=stored_session.data, sid=stored_session.sid)
        return MongoEngineSession(sid=str(uuid.uuid4()))

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            if session.modified:
                response.delete_cookie(app.session_cookie_name, domain=domain)
            return

        expiration = datetime.datetime.utcnow() + self.get_expiration_time(app, session)

        if session.modified:
            self.cls(sid=session.sid, data=session, expiration=expiration).save()

        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=expiration, httponly=True, domain=domain)
