import atexit, os.path, time, mongoengine, sys
import shutil, subprocess, tempfile
from flask import current_app
from pymongo import MongoClient, ReadPreference, errors, uri_parser
from subprocess import Popen, PIPE
from pymongo.errors import InvalidURI
from mongoengine import connection

__all__ = (
    'create_connection', 'disconnect', 'get_connection',
    'DEFAULT_CONNECTION_NAME', 'fetch_connection_settings',
    'InvalidSettingsError', 'get_db'
)

DEFAULT_CONNECTION_NAME = 'default-mongodb-connection'

_connection_settings = {}
_connections = {}
_tmpdir = None
_conn = None
_process = None
_app_instance = current_app

class InvalidSettingsError(Exception):
    pass

def disconnect(alias=DEFAULT_CONNECTION_NAME, preserved=False):
    global _connections, _process, _tmpdir

    if alias in _connections:
        conn = get_connection(alias=alias);
        client = conn.client
        if client:
            client.close()
        else:
            conn.close()
        del _connections[alias]

    if _process:
        _process.terminate()
        _process.wait()
        _process = None

    if (not preserved and _tmpdir):
        sock_file = 'mongodb-27111.sock'
        if os.path.exists(_tmpdir):
            shutil.rmtree(_tmpdir, ignore_errors=True)
        if os.path.exists(sock_file):
            os.remove("{0}/{1}".\
                format(tempfile.gettempdir(), sock_file))

def _validate_settings(is_test, temp_db, preserved, conn_host):
    """
    Validate unitest settings to ensure
    valid values are supplied before obtaining
    connection.

    """
    if (not isinstance(is_test, bool)
        or not isinstance(temp_db, bool)
        or not isinstance(preserved, bool)):
        msg = '`TESTING`, `TEMP_DB`, and `PRESERVE_TEMP_DB`'\
                ' must be boolean values'
        raise InvalidSettingsError(msg)

    elif not is_test and conn_host.startswith('mongomock://'):
        msg = "`MongoMock` connection is only required for `unittest`."\
                "To enable this set `TESTING` to true`."
        raise InvalidURI(msg)

    elif not is_test and temp_db or preserved:
        msg = '`TESTING` and/or `TEMP_DB` can be used '\
                'only when `TESTING` is set to true.'
        raise InvalidSettingsError(msg)

def __get_app_config(key):
    return (_app_instance.get(key, False)
            if isinstance(_app_instance, dict)
            else _app_instance.config.get(key, False))

def get_connection(alias=DEFAULT_CONNECTION_NAME, reconnect=False):
    global _connections
    set_global_attributes()

    if reconnect:
        disconnect(alias, _connection_settings.get('preserve_temp_db', False))

    # Establish new connection unless
    # already established
    if alias not in _connections:
        if alias not in _connection_settings:
            msg = 'Connection with alias "%s" has not been defined' % alias
            if alias == DEFAULT_CONNECTION_NAME:
                msg = 'You have not defined a default connection'
            raise ConnectionError(msg)

        conn_settings = _connection_settings[alias].copy()
        conn_host = conn_settings['host']
        db_name = conn_settings['name']

        conn_settings.pop('name', None)
        conn_settings.pop('username', None)
        conn_settings.pop('password', None)
        conn_settings.pop('authentication_source', None)

        is_test = __get_app_config('TESTING')
        temp_db = __get_app_config('TEMP_DB')
        preserved = __get_app_config('PRESERVE_TEMP_DB')

        # Validation
        _validate_settings(is_test, temp_db, preserved, conn_host)

        # Obtain connection
        if is_test:
            connection_class = None

            if temp_db:
                db_alias = conn_settings['alias']
                port = conn_settings['port']
                return _register_test_connection(port, db_alias, preserved)

            elif (conn_host.startswith('mongomock://') and
                mongoengine.VERSION < (0, 10, 6)):
                # Use MongoClient from mongomock
                try:
                    import mongomock
                except ImportError:
                    msg = 'You need mongomock installed to mock MongoEngine.'
                    raise RuntimeError(msg)

                # `mongomock://` is not a valid url prefix and
                # must be replaced by `mongodb://`
                conn_settings['host'] = \
                    conn_host.replace('mongomock://', 'mongodb://', 1)
                connection_class = mongomock.MongoClient
            else:
                # Let mongoengine handle the default
                _connections[alias] = mongoengine.connect(db_name, **conn_settings)
        else:
            # Let mongoengine handle the default
            _connections[alias] = mongoengine.connect(db_name, **conn_settings)

        try:
            connection = None
            connection_iter_items = _connection_settings.items() \
                if (sys.version_info >= (3, 0)) else _connection_settings.iteritems()

            # check for shared connections
            connection_settings_iterator = \
                ((db_alias, settings.copy()) for db_alias, settings in connection_iter_items)

            for db_alias, connection_settings in connection_settings_iterator:
                connection_settings.pop('name', None)
                connection_settings.pop('username', None)
                connection_settings.pop('password', None)

                if _connections.get(db_alias, None):
                    connection = _connections[db_alias]
                    break

                if connection:
                    _connections[alias] = connection
                else:
                    if connection_class:
                        _connections[alias] = connection_class(**conn_settings)

        except Exception as e:
            msg = "Cannot connect to database %s :\n%s" % (alias, e)
            raise ConnectionError(msg)

    return mongoengine.connection.get_db(alias)

def _sys_exec(cmd, shell=True, env=None):
    if env is None:
        env = os.environ

    a = Popen(cmd, shell=shell, stdout=PIPE, stderr=PIPE, env=env)
    a.wait()  # Wait for process to terminate
    if a.returncode:  # Not 0 => Error has occured
        raise Exception(a.communicate()[1])
    return a.communicate()[0]

def set_global_attributes():
    setattr(connection, '_connection_settings', _connection_settings)
    setattr(connection, '_connections', _connections)
    setattr(connection, 'disconnect', disconnect)

def get_db(alias=DEFAULT_CONNECTION_NAME, reconnect=False):
    set_global_attributes()
    return connection.get_db(alias, reconnect)

def _register_test_connection(port, db_alias, preserved):
    global _process, _tmpdir

    # Lets check MongoDB is installed locally
    # before making connection to it
    try:
        found = _sys_exec("mongod --version") or False
    except:
        msg = 'You need `MongoDB` service installed on localhost'\
              ' to create a TEMP_DB instance.'
        raise RuntimeError(msg)

    if found:
        # TEMP_DB setting uses 27111 as
        # default port
        if not port or port == 27017:
            port = 27111

        _tmpdir = current_app.config.get('TEMP_DB_LOC', tempfile.mkdtemp())
        print("@@ TEMP_DB_LOC  = %s" % _tmpdir)
        print("@@ TEMP_DB port = %s" % str(port))
        print("@@ TEMP_DB host = localhost")
        _conn = _connections.get(db_alias, None)

        if _conn is None:
            _process = subprocess.Popen([
                    'mongod', '--bind_ip', 'localhost',
                    '--port', str(port),
                    '--dbpath', _tmpdir,
                    '--nojournal', '--nohttpinterface',
                    '--noauth', '--smallfiles',
                    '--syncdelay', '0',
                    '--maxConns', '10',
                    '--nssize', '1', ],
                    stdout=open(os.devnull, 'wb'),
                    stderr=subprocess.STDOUT)
            atexit.register(disconnect, preserved=preserved)

            # wait for the instance db to be ready
            # before opening a Connection.
            for i in range(3):
                time.sleep(0.1)
                try:
                    _conn = MongoClient('localhost', port)
                except errors.ConnectionFailure:
                    continue
                else: break
            else:
                msg = 'Cannot connect to the mongodb test instance'
                raise mongoengine.ConnectionError(msg)
            _connections[db_alias] = _conn
        return _conn

def _resolve_settings(conn_setting, removePass=True):

    if conn_setting and isinstance(conn_setting, dict):
        conn_setting = dict(((k[8:] if k.startswith("MONGODB_") else k), v) for k, v in conn_setting.items() if v is not None)
        conn_setting = dict((k.lower(), v) for k, v in conn_setting.items())

        alias = conn_setting.get('alias', DEFAULT_CONNECTION_NAME)
        db = conn_setting.get('db', 'test')
        host = conn_setting.get('host', 'localhost')
        port = conn_setting.get('port', 27017)
        username = conn_setting.get('username', None)
        password = conn_setting.get('password', None)
        # Default to ReadPreference.PRIMARY if no read_preference is supplied
        read_preference = conn_setting.get('read_preference', ReadPreference.PRIMARY)

        resolved = {}
        resolved['read_preference'] = read_preference
        resolved['alias'] = alias
        resolved['name'] = db
        resolved['host'] = host
        resolved['password'] = password
        resolved['port'] = port
        resolved['username'] = username
        if conn_setting.pop('replicaset', None):
            resolved['replicaSet'] = conn_setting.pop('replicaset', None)

        host = resolved['host']
        # Handle uri style connections
        if host.startswith('mongodb://'):
            uri_dict = uri_parser.parse_uri(host)
            if uri_dict['database']:
                resolved['host'] = uri_dict['database']
            if uri_dict['password']:
                resolved['password'] = uri_dict['password']
            if uri_dict['username']:
                resolved['username'] = uri_dict['username']
            if uri_dict['options'] and uri_dict['options']['replicaset']:
                resolved['replicaSet'] = uri_dict['options']['replicaset']

        if removePass and password:
            resolved.pop('password')

        return resolved
    return conn_setting

def fetch_connection_settings(config, removePass=True):
    """
    Fetch DB connection settings from FlaskMongoEngine
    application instance configuration. For backward
    compactibility reasons the settings name has not
    been replaced.

    It has instead been mapped correctly
    to avoid connection issues.

    @param config:          FlaskMongoEngine instance config

    @param removePass:      Flag to instruct the method to either
                            remove password or maintain as is.
                            By default a call to this method returns
                            settings without password.
    """

    if 'MONGODB_SETTINGS' in config:
        settings = config['MONGODB_SETTINGS']
        if isinstance(settings, list):
            # List of connection settings.
            settings_list = []
            for setting in settings:
                settings_list.append(_resolve_settings(setting, removePass))
            return settings_list
        else:
            # Connection settings provided as a dictionary.
            return _resolve_settings(settings, removePass)
    else:
        # Connection settings provided in standard format.
        return _resolve_settings(config, removePass)

def create_connection(config, app):
    """
    Connection is created based on application configuration
    setting. Application settings which is enabled as TESTING
    can submit MongoMock URI or enable TEMP_DB setting to provide
    default temporary MongoDB instance on localhost for testing
    purposes. This connection is initiated with a separate temporary
    directory location.

    Unless PRESERVE_TEST_DB is setting is enabled in application
    configuration, temporary MongoDB instance will be deleted when
    application instance goes out of scope.

    Setting to request MongoMock instance connection:
        >> app.config['TESTING'] = True
        >> app.config['MONGODB_ALIAS'] = 'unittest'
        >> app.config['MONGODB_HOST'] = 'mongo://localhost'

    Setting to request temporary localhost instance of MongoDB
    connection:
        >> app.config['TESTING'] = True
        >> app.config['TEMP_DB'] = True

    To avoid temporary localhost instance of MongoDB been deleted
    when application go out of scope:
        >> app.config['PRESERVE_TEMP_DB'] = true

    You can specify the location of the temporary database instance
    by setting TEMP_DB_LOC. If not specified, a default temp directory
    location will be generated and used instead:
        >> app.config['TEMP_DB_LOC'] = '/path/to/temp_dir/'

    @param config: Flask-MongoEngine application configuration.
    @param app: instance of flask.Flask
    """
    global _connection_settings, _app_instance
    _app_instance = app if app else config

    if config is None or not isinstance(config, dict):
        raise Exception("Invalid application configuration");

    conn_settings = fetch_connection_settings(config, False)

    # Handle multiple connections recursively
    if isinstance(conn_settings, list):
        connections = {}
        for conn_setting in conn_settings:
            alias = conn_setting['alias']
            _connection_settings[alias] = conn_setting
            connections[alias] = get_connection(alias)
        return connections
    else:
        alias = conn_settings.get('alias', DEFAULT_CONNECTION_NAME)
        _connection_settings[alias] = conn_settings
        return get_connection(alias)
