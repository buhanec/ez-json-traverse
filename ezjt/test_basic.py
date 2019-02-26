"""Just enough to prove it kind of works."""

import unittest

from . import EZJL, EZJD, as_traversable


class TestEquality(unittest.TestCase):

    def test_list_traversable(self):
        val = [0, [1]]
        self.assertEqual(EZJL(val), as_traversable(val))

    def test_dict_traversable(self):
        val = {'0': {'1': '2'}}
        self.assertEqual(EZJD(val), as_traversable(val))


class TestListAccess(unittest.TestCase):
    raw = [[0, 1], [2, 3], [4, 5]]
    val = EZJL(raw)

    def test_int(self):
        self.assertEqual(self.val[0], EZJL([0, 1],
                                           path='0',
                                           parent=self.val))
        self.assertEqual(self.val[1], EZJL([2, 3],
                                           path='1',
                                           parent=self.val))
        self.assertEqual(self.val[2], EZJL([4, 5],
                                           path='2',
                                           parent=self.val))
        self.assertEqual(self.val[-1], EZJL([4, 5],
                                            path='-1',
                                            parent=self.val))

    def test_int_as_str(self):
        self.assertEqual(self.val['0'], EZJL([0, 1],
                                             path='0',
                                             parent=self.val))
        self.assertEqual(self.val['1'], EZJL([2, 3],
                                             path='1',
                                             parent=self.val))
        self.assertEqual(self.val['2'], EZJL([4, 5],
                                             path='2',
                                             parent=self.val))
        self.assertEqual(self.val['-1'], EZJL([4, 5],
                                              path='-1',
                                              parent=self.val))

    def test_slice(self):
        self.assertEqual(self.val[0:3], EZJL(self.raw,
                                             path='0:3',
                                             parent=self.val))
        self.assertEqual(self.val[:], EZJL(self.raw,
                                           path=':',
                                           parent=self.val))
        self.assertEqual(self.val[0:1], EZJL([[0, 1]],
                                             path='0:1',
                                             parent=self.val))

    def test_slice_as_str(self):
        self.assertEqual(self.val['0:3'], EZJL(self.raw,
                                               path='0:3',
                                               parent=self.val))
        self.assertEqual(self.val[':'], EZJL(self.raw,
                                             path=':',
                                             parent=self.val))
        self.assertEqual(self.val['0:1'], EZJL([[0, 1]],
                                               path='0:1',
                                               parent=self.val))

    def test_simple_nesting(self):
        self.assertEqual(self.val['0.1'], 1)
        self.assertEqual(self.val['1.1'], 3)

    def test_map(self):
        thing = EZJL([[[0], [1], [2]]])
        self.assertEqual(self.val['0:3^.1'], EZJL([1, 3, 5],
                                                  path='0:3^.1',
                                                  parent=self.val))
        self.assertEqual(thing['0^.0'], EZJL([0, 1, 2],
                                             path='0^.0',
                                             parent=thing))


class TestDictAccess(unittest.TestCase):

    val = EZJD({
        'a': {'name': 'Jane', 'age': 12},
        'b': {'name': 'John', 'age': 14},
        'c': {'name': 'Jill', 'age': 10}
    })

    def test_simple(self):
        self.assertEqual(self.val['a'], EZJD({'name': 'Jane', 'age': 12},
                                             path='a',
                                             parent=self.val))
        self.assertEqual(self.val['b'], EZJD({'name': 'John', 'age': 14},
                                             path='b',
                                             parent=self.val))
        self.assertEqual(self.val['c'], EZJD({'name': 'Jill', 'age': 10},
                                             path='c',
                                             parent=self.val))

    def test_nested(self):
        self.assertEqual(self.val['a.name'], 'Jane')
        self.assertEqual(self.val['a.age'], 12)

    def test_map(self):
        self.assertEqual(self.val['^.__key'], EZJL(['a', 'b', 'c'],
                                                   path='^.__key',
                                                   parent=self.val))
        self.assertEqual(self.val['^.name'], EZJL(['Jane', 'John', 'Jill'],
                                                  path='^.name',
                                                  parent=self.val))
        self.assertEqual(self.val['^.age'], EZJL([12, 14, 10],
                                                 path='^.age',
                                                 parent=self.val))


class TestProperties(unittest.TestCase):

    dict_ = EZJD({
        'a': {'name': 'Jane', 'age': {'unit': 'year', 'value': 12}},
        'b': {'name': 'John', 'age': {'unit': 'year', 'value': 14}},
        'c': {'name': 'Jill', 'age': {'unit': 'year', 'value': 10}}
    })

    list_ = EZJL([[0, [1, 2]], [1, [2, 3]], [2, [3, 4]]])

    def test_dict_path(self):
        self.assertEqual(self.dict_['b.age'].path, 'b.age')
        self.assertEqual(self.dict_['b.age'].key, 'age')
        self.assertEqual(self.dict_['^.age.value'].path, '^.age.value')
        self.assertEqual(self.dict_['^.age.value'].key, 'value')

    def test_list_path(self):
        self.assertEqual(self.list_['1.1'].path, '1.1')
        self.assertEqual(self.list_['1.1'].key, '1')
        self.assertEqual(self.list_[':^.1.0'].path, ':^.1.0')
        self.assertEqual(self.list_[':^.1.0'].key, '0')

    def test_dict_ancestors(self):
        self.assertEqual(self.dict_['b.age'].parent, self.dict_['b'])
        self.assertEqual(self.dict_['b.age'].root, self.dict_)
        self.assertEqual(self.dict_['^.age.value'].root, self.dict_)

    def test_list_ancestors(self):
        self.assertEqual(self.list_['1.1'].parent, self.list_['1'])
        self.assertEqual(self.list_['1.1'].root, self.list_)
        self.assertEqual(self.list_[':^.1.0'].root, self.list_)


class TestGet(unittest.TestCase):

    dict_ = EZJD({
        'a': {'name': 'Jane', 'age': {'unit': 'year', 'value': 12}},
        'b': {'name': 'John', 'age': {'unit': 'year', 'value': 14}},
        'c': {'name': 'Jill', 'age': {'unit': 'year', 'value': 10}}
    })

    list_ = EZJL([[0, [1, 2]], [1, [2, 3]], [2, [3, 4]]])

    def test_dict_exists(self):
        self.assertEqual(self.dict_.get('a.name'), 'Jane')

    def test_dict_not_exists(self):
        self.assertEqual(self.dict_.get('a.gender'), None)
        self.assertEqual(self.dict_.get('a.gender', 'Unknown'), 'Unknown')

    def test_list_exists(self):
        self.assertEqual(self.list_.get('0.1.0'), 1)

    def test_list_not_exists(self):
        self.assertEqual(self.list_.get('0.1.2'), None)
        self.assertEqual(self.list_.get('0.1.2', -1), -1)


if __name__ == '__main__':
    unittest.main()
