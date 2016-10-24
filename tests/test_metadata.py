import imp
import os
import unittest

from tests import FlaskMongoEngineTestCase


class MetaDataTestCase(FlaskMongoEngineTestCase):

    def setUp(self):
        super(MetaDataTestCase, self).setUp()
        self.metadata = None
        self.base_dir = os.path.split(os.path.dirname(__file__))[0]

    def test_metadata(self):
        self.assertTrue(self.base_dir is not None)

        metadata_script = os.path.join(self.base_dir, "flask_mongoengine", "metadata.py")
        self.assertTrue(metadata_script is not None)

        self.assertTrue(self.metadata is None)
        self.metadata = imp.load_source('metadata', metadata_script)

        self.assertTrue(self.metadata is not None)
        self.assertTrue(self.metadata.__version__ is not None)

        # Ensures change in version is legitimate
        msg = "Version do not match value in metadata.py `VERSION`"

        self.assertEqual("0.8", self.metadata.__version__, msg)

if __name__ == '__main__':
    unittest.main()
