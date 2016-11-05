import unittest
from werkzeug.exceptions import NotFound

from flask_mongoengine import ListFieldPagination, MongoEngine, Pagination
from tests import FlaskMongoEngineTestCase


class PaginationTestCase(FlaskMongoEngineTestCase):

    def setUp(self):
        super(PaginationTestCase, self).setUp()
        self.db_name = 'test_db'
        self.app.config['MONGODB_DB'] = self.db_name
        self.app.config['TESTING'] = True
        self.app.config['CSRF_ENABLED'] = False
        self.db = MongoEngine()
        self.db.init_app(self.app)

    def tearDown(self):
        try:
            self.db.connection.drop_database(self.db_name)
        except:
            self.db.connection.client.drop_database(self.db_name)

    def test_queryset_paginator(self):
        with self.app.test_request_context('/'):
            db = self.db

            class Post(db.Document):
                title = db.StringField(required=True, max_length=200)

            for i in range(42):
                Post(title="post: %s" % i).save()

        self.assertRaises(NotFound, Pagination, Post.objects, 0, 10)
        self.assertRaises(NotFound, Pagination, Post.objects, 6, 10)

        paginator = Pagination(Post.objects, 1, 10)
        self._test_paginator(paginator)

    def test_paginate_plain_list(self):

        self.assertRaises(NotFound, Pagination, range(1, 42), 0, 10)
        self.assertRaises(NotFound, Pagination, range(1, 42), 6, 10)

        paginator = Pagination(range(1, 42), 1, 10)
        self._test_paginator(paginator)

    def test_list_field_pagination(self):

        with self.app.test_request_context('/'):
            db = self.db

            class Post(db.Document):
                title = db.StringField(required=True, max_length=200)
                comments = db.ListField(db.StringField())
                comment_count = db.IntField()

            comments = ["comment: %s" % i for i in range(42)]
            post = Post(title="post has comments", comments=comments,
                        comment_count=len(comments)).save()

            # Check without providing a total
            paginator = ListFieldPagination(Post.objects, post.id, "comments",
                                            1, 10)
            self._test_paginator(paginator)

            # Check with providing a total (saves a query)
            paginator = ListFieldPagination(Post.objects, post.id, "comments",
                                            1, 10, post.comment_count)
            self._test_paginator(paginator)

            paginator = post.paginate_field('comments', 1, 10)
            self._test_paginator(paginator)

    def _test_paginator(self, paginator):
            self.assertEqual(5, paginator.pages)
            self.assertEqual([1, 2, 3, 4, 5], list(paginator.iter_pages()))

            for i in [1, 2, 3, 4, 5]:

                if i == 1:
                    self.assertRaises(NotFound, paginator.prev)
                    self.assertFalse(paginator.has_prev)
                else:
                    self.assertTrue(paginator.has_prev)

                if i == 5:
                    self.assertRaises(NotFound, paginator.next)
                    self.assertFalse(paginator.has_next)
                else:
                    self.assertTrue(paginator.has_next)

                if i == 3:
                    self.assertEqual([None, 2, 3, 4, None],
                                     list(paginator.iter_pages(0, 1, 1, 0)))

                self.assertEqual(i, paginator.page)
                self.assertEqual(i - 1, paginator.prev_num)
                self.assertEqual(i + 1, paginator.next_num)

                # Paginate to the next page
                if i < 5:
                    paginator = paginator.next()


if __name__ == '__main__':
    unittest.main()
