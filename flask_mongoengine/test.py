from unittest import TestCase


def tc_factory(db, BaseClass=TestCase):
    TestCaseClass = type("TestCase", (BaseClass,), {})

    return TestCaseClass
