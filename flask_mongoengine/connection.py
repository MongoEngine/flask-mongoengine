import mongoengine
from pymongo import ReadPreference, uri_parser

__all__ = (
    'create_connections', 'get_connection_settings', 'InvalidSettingsError',
)


class InvalidSettingsError(Exception):
    pass


def _sanitize_settings(settings):
    """Given a dict of connection settings, sanitize the keys and fall
    back to some sane defaults.
    """
    # Remove the "MONGODB_" prefix and make all settings keys lower case.
    resolved_settings = {}
    for k, v in settings.items():
        if k.startswith('MONGODB_'):
            k = k[len('MONGODB_'):]
        k = k.lower()
        resolved_settings[k] = v

    # Handle uri style connections
    if "://" in resolved_settings.get('host', ''):
        uri_dict = uri_parser.parse_uri(resolved_settings['host'])
        resolved_settings['db'] = uri_dict['database']

    # Add a default name param or use the "db" key if exists
    if resolved_settings.get('db'):
        resolved_settings['name'] = resolved_settings.pop('db')
    else:
        resolved_settings['name'] = 'test'

    # Add various default values.
    resolved_settings['alias'] = resolved_settings.get('alias', mongoengine.DEFAULT_CONNECTION_NAME)  # TODO do we have to specify it here? MongoEngine should take care of that
    resolved_settings['host'] = resolved_settings.get('host', 'localhost')  # TODO this is the default host in pymongo.mongo_client.MongoClient, we may not need to explicitly set a default here
    resolved_settings['port'] = resolved_settings.get('port', 27017)  # TODO this is the default port in pymongo.mongo_client.MongoClient, we may not need to explicitly set a default here

    # Default to ReadPreference.PRIMARY if no read_preference is supplied
    resolved_settings['read_preference'] = resolved_settings.get('read_preference', ReadPreference.PRIMARY)

    # Rename "replicaset" to "replicaSet" if it exists in the dict
    # TODO is this necessary? PyMongo normalizes the options and makes them
    # all lowercase via pymongo.common.validate (which is called in
    # MongoClient.__init__), so both "replicaset and "replicaSet" should be
    # valid
    # if 'replicaset' in resolved_settings:
    #    resolved_settings['replicaSet'] = resolved_settings.pop('replicaset')

    # Clean up empty values
    for k, v in list(resolved_settings.items()):
        if v is None:
            del resolved_settings[k]

    return resolved_settings


def get_connection_settings(config):
    """
    Given a config dict, return a sanitized dict of MongoDB connection
    settings that we can then use to establish connections. For new
    applications, settings should exist in a "MONGODB_SETTINGS" key, but
    for backward compactibility we also support several config keys
    prefixed by "MONGODB_", e.g. "MONGODB_HOST", "MONGODB_PORT", etc.
    """
    # Sanitize all the settings living under a "MONGODB_SETTINGS" config var
    if 'MONGODB_SETTINGS' in config:
        settings = config['MONGODB_SETTINGS']

        # If MONGODB_SETTINGS is a list of settings dicts, sanitize each
        # dict separately.
        if isinstance(settings, list):
            # List of connection settings.
            settings_list = []
            for setting in settings:
                settings_list.append(_sanitize_settings(setting))
            return settings_list

        # Otherwise, it should be a single dict describing a single connection.
        else:
            return _sanitize_settings(settings)

    # If "MONGODB_SETTINGS" doesn't exist, sanitize all the keys starting with
    # "MONGODB_" as if they all describe a single connection.
    else:
        config = dict((k, v) for k, v in config.items() if k.startswith('MONGODB_'))  # ugly dict comprehention in order to support python 2.6
        return _sanitize_settings(config)


def create_connections(config):
    """
    Given Flask application's config dict, extract relevant config vars
    out of it and establish MongoEngine connection(s) based on them.
    """
    # Validate that the config is a dict
    if config is None or not isinstance(config, dict):
        raise InvalidSettingsError('Invalid application configuration')

    # Get sanitized connection settings based on the config
    conn_settings = get_connection_settings(config)

    # If conn_settings is a list, set up each item as a separate connection
    # and return a dict of connection aliases and their connections.
    if isinstance(conn_settings, list):
        connections = {}
        for each in conn_settings:
            alias = each['alias']
            connections[alias] = _connect(each)
        return connections

    # Otherwise, return a single connection
    return _connect(conn_settings)


def _connect(conn_settings):
    """Given a dict of connection settings, create a connection to
    MongoDB by calling mongoengine.connect and return its result.
    """
    db_name = conn_settings.pop('name')
    return mongoengine.connect(db_name, **conn_settings)
