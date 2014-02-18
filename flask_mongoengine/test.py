from unittest import TestCase


def cleanup_db(db):
    for collection_name in db.collection_names():
        if collection_name != 'system.indexes':
            db.drop_collection(collection_name)


def tc_factory(db, BaseClass=TestCase):

    def __init__(self, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)

        db.configure_test_db()
        self.test_app = db.app

        db_name = self.test_app.config.get("MONGODB_SETTINGS")["DB"]
        test_db_name = db_name if "test_" in db_name else "test_" + db_name
        mongo_db = db.connection[test_db_name]
        self.addCleanup(cleanup_db, mongo_db)

    TestCaseClass = type("TestCase", (BaseClass,), {"__init__": __init__})

    return TestCaseClass
