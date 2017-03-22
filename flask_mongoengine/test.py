from unittest import TestCase


def tc_factory(db, BaseClass=TestCase):

    _dict = {}
    has_addCleanup = hasattr(BaseClass, "addCleanup")

    def __init__(self, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)

        db.configure_test_db()
        self.test_app = db.app

        if has_addCleanup:
            self.addCleanup(cleanup_db, self)

    def cleanup_db(self):
        db_name = self.test_app.config.get("MONGODB_SETTINGS")["DB"]
        test_db_name = db_name if "test_" in db_name else "test_" + db_name
        mongo_db = db.connection[test_db_name]

        for collection_name in mongo_db.collection_names():
            if collection_name != 'system.indexes':
                mongo_db.drop_collection(collection_name)

    _dict = {"__init__": __init__}
    if not has_addCleanup:
        _dict.update({"tearDown": cleanup_db})
    TestCaseClass = type("TestCase", (BaseClass,), _dict)

    return TestCaseClass
