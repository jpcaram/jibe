import unittest
from jibe import NotifyList2


class MyTestCase(unittest.TestCase):

    def setUp(self) -> None:
        self.x = None

    def test_something(self):

        n = NotifyList2([1, 2, 'a'])

        def callback_append(obj, *args, **kwargs):
            print("callback_append() got called", args, kwargs)
            self.x = args[0]

        n._on_append_callbacks.append(callback_append)

        self.x = None
        n.append('k')

        self.assertEqual('k', self.x)

        self.x = None
        n[0] = 'p'

        self.assertNotEqual('p', self.x)

        def callback_setitem(obj, *args, **kwargs):
            print("callback_setitem() got called", args, kwargs)
            self.x = args[1]  # 0 is the index

        n._on_setitem_callbacks.append(callback_setitem)

        self.x = None
        n[0] = 'p'

        self.assertEqual('p', self.x)

    def test_extend(self):

        n = NotifyList2([1, 2, 'a'])

        def callback_extend(obj, *args, **kwargs):
            print("callback_extend() got called", args, kwargs)
            self.x = args[0]

        n._on_extend_callbacks.append(callback_extend)

        def callback_setitem(obj, *args, **kwargs):
            print("callback_setitem() got called", args, kwargs)
            self.x = args[1]  # 0 is the index

        n._on_setitem_callbacks.append(callback_setitem)

        def callback_append(obj, *args, **kwargs):
            print("callback_append() got called", args, kwargs)
            self.x = args[0]

        n._on_append_callbacks.append(callback_append)

        def callback_iadd(obj, *args, **kwargs):
            """When obj += [...]"""
            print("callback_iadd() got called", args, kwargs)
            self.x = args[0]

        n._on_iadd_callbacks.append(callback_iadd)

        self.x = None
        n += [5, 7]  # iadd

        self.assertEqual([5, 7], self.x)

        self.x = None
        n.extend(['h'])

        self.assertEqual(['h'], self.x)


if __name__ == '__main__':
    unittest.main()
