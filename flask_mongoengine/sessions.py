"""MongoDB Session Interface"""
import typing as t
from datetime import datetime, timedelta
import uuid

from bson.tz_util import utc
from flask.sessions import SessionInterface, SessionMixin
from werkzeug.datastructures import CallbackDict

# Type checking
if t.TYPE_CHECKING:
    from flask.app import Flask
    from flask.wrappers import Request, Response

__all__ = ("MongoEngineSession", "MongoEngineSessionInterface")


class MongoEngineSession(CallbackDict, SessionMixin):
    def __init__(self, initial=None, sid=None):
        def on_update(self):
            self.modified = True

        CallbackDict.__init__(self, initial, on_update)
        self.sid = sid
        self.modified = False


class MongoEngineSessionInterface(SessionInterface):
    """SessionInterface for mongoengine"""

    def __init__(self, db, collection="session"):
        """
        The MongoSessionInterface

        :param db: The app's db eg: MongoEngine()
        :param collection: The session collection name defaults to "session"
        """

        if not isinstance(collection, str):
            raise ValueError("Collection argument should be string")

        class DBSession(db.Document):
            sid = db.StringField(primary_key=True)
            data = db.DictField()
            expiration = db.DateTimeField()
            meta = {
                "allow_inheritance": False,
                "collection": collection,
                "indexes": [
                    {
                        "fields": ["expiration"],
                        "expireAfterSeconds": 60 * 60 * 24 * 7 * 31,
                    }
                ],
            }

        self.cls = DBSession

    def get_expiration_time(self, app: "Flask", session: SessionMixin) -> datetime:
        now = datetime.utcnow().replace(tzinfo=utc)
        if session.permanent:
            return now + app.permanent_session_lifetime
        # Fallback to 1 day session ttl, if SESSION_TTL not set.
        return now + timedelta(**app.config.get("SESSION_TTL", {"days": 1}))

    def open_session(self, app: "Flask", request: "Request") -> MongoEngineSession:
        val = request.cookies.get(self.get_cookie_name(app))
        if not val:
            return MongoEngineSession(sid=str(uuid.uuid4()))
        stored_session = self.cls.objects(sid=val).first()
        if not stored_session:
            return MongoEngineSession(sid=str(uuid.uuid4()))
        expiration = stored_session.expiration
        if not expiration.tzinfo:
            expiration = expiration.replace(tzinfo=utc)
        if expiration > datetime.utcnow().replace(tzinfo=utc):
            return MongoEngineSession(
                initial=stored_session.data, sid=stored_session.sid
            )
        return MongoEngineSession(sid=str(uuid.uuid4()))

    def save_session(  # type: ignore[override]
        self, app: "Flask", session: MongoEngineSession, response: "Response"
    ):
        name = self.get_cookie_name(app)
        domain = self.get_cookie_domain(app)
        path = self.get_cookie_path(app)
        secure = self.get_cookie_secure(app)
        samesite = self.get_cookie_samesite(app)

        # If the session is modified to be empty, remove the cookie.
        # If the session is empty, return without setting the cookie.
        if not session:
            if session.modified:
                response.delete_cookie(
                    name, domain=domain, path=path, secure=secure, samesite=samesite
                )
            return

        # Add a "Vary: Cookie" header if the session was accessed at all.
        if session.accessed:
            response.vary.add("Cookie")

        if not self.should_set_cookie(app, session):
            return

        httponly = self.get_cookie_httponly(app)
        expires = self.get_expiration_time(app, session)

        if session.modified:
            self.cls(sid=session.sid, data=session, expiration=expires).save()

        response.set_cookie(
            key=name,
            value=session.sid,
            expires=expires,
            httponly=httponly,
            domain=domain,
            path=path,
            secure=secure,
            samesite=samesite,
        )
