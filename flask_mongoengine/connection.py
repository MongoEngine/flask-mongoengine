"""Module responsible for connection setup."""
import warnings
from typing import List

import mongoengine

__all__ = (
    "create_connections",
    "get_connection_settings",
)


def _get_name(setting_name: str) -> str:
    """
    Return known pymongo setting name, or lower case name for unknown.

    This problem discovered in issue #451. As mentioned there pymongo settings are not
    case-sensitive, but mongoengine use exact name of some settings for matching,
    overwriting pymongo behaviour.

    This function address this issue, and potentially address cases when pymongo will
    become case-sensitive in some settings by same reasons as mongoengine done.

    Based on pymongo 4.1.1 settings.
    """
    KNOWN_CAMEL_CASE_SETTINGS = {
        "directconnection": "directConnection",
        "maxpoolsize": "maxPoolSize",
        "minpoolsize": "minPoolSize",
        "maxidletimems": "maxIdleTimeMS",
        "maxconnecting": "maxConnecting",
        "sockettimeoutms": "socketTimeoutMS",
        "connecttimeoutms": "connectTimeoutMS",
        "serverselectiontimeoutms": "serverSelectionTimeoutMS",
        "waitqueuetimeoutms": "waitQueueTimeoutMS",
        "heartbeatfrequencyms": "heartbeatFrequencyMS",
        "retrywrites": "retryWrites",
        "retryreads": "retryReads",
        "zlibcompressionlevel": "zlibCompressionLevel",
        "uuidrepresentation": "uuidRepresentation",
        "srvservicename": "srvServiceName",
        "wtimeoutms": "wTimeoutMS",
        "replicaset": "replicaSet",
        "readpreference": "readPreference",
        "readpreferencetags": "readPreferenceTags",
        "maxstalenessseconds": "maxStalenessSeconds",
        "authsource": "authSource",
        "authmechanism": "authMechanism",
        "authmechanismproperties": "authMechanismProperties",
        "tlsinsecure": "tlsInsecure",
        "tlsallowinvalidcertificates": "tlsAllowInvalidCertificates",
        "tlsallowinvalidhostnames": "tlsAllowInvalidHostnames",
        "tlscafile": "tlsCAFile",
        "tlscertificatekeyfile": "tlsCertificateKeyFile",
        "tlscrlfile": "tlsCRLFile",
        "tlscertificatekeyfilepassword": "tlsCertificateKeyFilePassword",
        "tlsdisableocspendpointcheck": "tlsDisableOCSPEndpointCheck",
        "readconcernlevel": "readConcernLevel",
    }
    _setting_name = KNOWN_CAMEL_CASE_SETTINGS.get(setting_name.lower())
    return setting_name.lower() if _setting_name is None else _setting_name


def _sanitize_settings(settings: dict) -> dict:
    """Remove ``MONGODB_`` prefix from dict values, to correct bypass to mongoengine."""
    resolved_settings = {}
    for k, v in settings.items():
        # Replace with k.lower().removeprefix("mongodb_") when python 3.8 support ends.
        key = _get_name(k[8:]) if k.lower().startswith("mongodb_") else _get_name(k)
        resolved_settings[key] = v

    return resolved_settings


def get_connection_settings(config: dict) -> List[dict]:
    """
    Given a config dict, return a sanitized dict of MongoDB connection
    settings that we can then use to establish connections. For new
    applications, settings should exist in a ``MONGODB_SETTINGS`` key, but
    for backward compatibility we also support several config keys
    prefixed by ``MONGODB_``, e.g. ``MONGODB_HOST``, ``MONGODB_PORT``, etc.
    """

    # If no "MONGODB_SETTINGS", sanitize the "MONGODB_" keys as single connection.
    if "MONGODB_SETTINGS" not in config:
        warnings.warn(
            (
                "Passing flat configuration is deprecated. Please check "
                "http://docs.mongoengine.org/projects/flask-mongoengine/flask_config.html "
                "for more info."
            ),
            DeprecationWarning,
            stacklevel=2,
        )
        config = {k: v for k, v in config.items() if k.lower().startswith("mongodb_")}
        return [_sanitize_settings(config)]

    # Sanitize all the settings living under a "MONGODB_SETTINGS" config var
    settings = config["MONGODB_SETTINGS"]

    # If MONGODB_SETTINGS is a list of settings dicts, sanitize each dict separately.
    if isinstance(settings, list):
        return [_sanitize_settings(settings_dict) for settings_dict in settings]

    # Otherwise, it should be a single dict describing a single connection.
    return [_sanitize_settings(settings)]


def create_connections(config: dict):
    """
    Given Flask application's config dict, extract relevant config vars
    out of it and establish MongoEngine connection(s) based on them.
    """
    # Validate that the config is a dict and dict is not empty
    if not config or not isinstance(config, dict):
        raise TypeError(f"Config dictionary expected, but {type(config)} received.")

    # Get sanitized connection settings based on the config
    connection_settings = get_connection_settings(config)

    connections = {}
    for connection_setting in connection_settings:
        alias = connection_setting.setdefault(
            "alias",
            mongoengine.DEFAULT_CONNECTION_NAME,
        )
        connection_setting.setdefault("uuidRepresentation", "standard")
        connections[alias] = mongoengine.connect(**connection_setting)

    return connections
