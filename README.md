# ez-json-traverse [![Build Status](https://img.shields.io/travis/buhanec/ez-json-traverse/master.svg?style=flat-square&label=Travis%20Build)](https://travis-ci.org/buhanec/ez-json-traverse) [![Supported Python Version](https://img.shields.io/pypi/pyversions/ez-json-traverse.svg?style=flat-square)](https://pypi.org/project/ez-json-traverse/) [![License](https://img.shields.io/pypi/l/ez-json-traverse.svg?style=flat-square)](https://pypi.org/project/ez-json-traverse/)

For easier traversing and exploration of JSON structures.

Provides a traversable sequence `EZJL`, traversable mapping `EZJD` and convenience methods like `as_traversable`.

## Starting off

    $ pip install ez-json-traverse
    
followed by

```python 
from ezjt import as_traversable
```

## Dict stuff

```python
d = {
    'a': {'name': 'Jane', 'age': {'unit': 'year', 'value': 12}},
    'b': {'name': 'John', 'age': {'unit': 'year', 'value': 14}},
    'c': {'name': 'Jill', 'age': {'unit': 'year', 'value': 10}}
}

t = as_traversable(d, sep='.', map_char='^')  # EZJD

# Normal key access
t['a']  # EZJD of {'name': 'Jane', 'age': {'unit': 'year', 'value': 12}}

# Path key access
t['a.name']  # 'Jane'

# Mapping across values
t['^.age.value']  # EZJD of [12, 14, 10]
```

## List stuff

```python
l = [[0, [1, 2]], [1, [2, 3]], [2, [3, 4]]]

t = as_traversable(l, sep='.', map_char='^')  # EZJL

# Normal key access
t[0]  # EZJL of [0, [1, 2]]
t['0']  # EZJL of [0, [1, 2]]

# Path key access
t['0.1.0']  # 1

# Mapping across values
t[':^.1.0']  # EZJL of [1, 2, 3]
t['1:-1^.1.0']  # EZJL of [2] 
```

## Other conveniences

```python
t = as_traversable(..., sep='.', map_char='^')  # EZJL

t.parent  # Parent container
t.root  # Root container
t.path  # Path from root container to current traversable
t.key  # Final key or index of current traversable
```
