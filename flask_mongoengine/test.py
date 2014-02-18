from unittest import TestCase


def tc_factory(db, BaseClass=TestCase):

    def __init__(self, *args, **kwargs):
        BaseClass.__init__(self, *args, **kwargs)

        db.configure_test_db()
        self.test_app = db.app

    TestCaseClass = type("TestCase", (BaseClass,), {"__init__": __init__})

    return TestCaseClass
