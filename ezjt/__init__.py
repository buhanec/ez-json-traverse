"""Easier JSON navigation and exploration."""

from itertools import chain
from pprint import pformat
from typing import Any, Dict, Iterator, List, Mapping, Optional, Sequence, Union


__all__ = ('EZJL', 'EZJD', 'as_traversable', 'traverse')

EZJsonValues = Optional[Union['EZJL', 'EZJD', str, float, int]]

DEFAULT_SEP = '.'
DEFAULT_MAP = '^'
DEFAULT_MAP_KEY = '__key'


def _slice_to_str(slice_: slice) -> str:
    start = slice_.start if slice_.start is not None else ''
    stop = slice_.stop if slice_.stop is not None else ''
    if slice_.step is not None:
        return f'{start}:{stop}:{slice_.step}'
    else:
        return f'{start}:{stop}'


def _str_to_slice(str_: str) -> slice:
    return slice(*map(lambda s: int(s) if s else None, str_.split(':')))


def traverse(value, path, *,
             traversed: Sequence[str] = tuple(),
             sep: str = DEFAULT_SEP,
             map_char: str = DEFAULT_MAP,
             dict_key_key: str = DEFAULT_MAP_KEY):
    try:
        parent = as_traversable(value,
                                parent=None,
                                path='',
                                sep=sep,
                                map_char=map_char,
                                dict_key_key=dict_key_key)
    except ValueError as e:
        raise ValueError('bad value') from e

    # Non-string path
    if isinstance(path, (int, slice)):
        retval = value[path]
        if isinstance(path, int):
            path_str = str(path)
        else:
            path_str = _slice_to_str(path)

        if isinstance(retval, (list, dict)):
            return as_traversable(retval,
                                  parent=parent,
                                  path=path_str,
                                  sep=sep,
                                  map_char=map_char,
                                  dict_key_key=dict_key_key)
        return retval
    if not isinstance(path, str):
        error_msg = f'Unsupported path {path!r} of type {type(path).__name__}'
        if isinstance(value, list):
            raise IndexError(error_msg)
        raise KeyError(error_msg)

    traversed = list(traversed)
    parent = None
    remaining = path.split(sep)
    while remaining:
        bit = remaining.pop(0)
        error_msg = f'Error traversing {path!r}, failed from {sep.join(traversed)!r} to {bit!r}: '  # noqa

        # Parent for next iter
        try:
            parent = as_traversable(value,
                                    parent=parent,
                                    path=sep.join(traversed),
                                    sep=sep,
                                    map_char=map_char,
                                    dict_key_key=dict_key_key)
        except ValueError as e:
            raise ValueError(error_msg + 'bad value') from e

        # Now that parent is created append that bit
        traversed.append(bit)

        # Flag to map over return value
        map_ret = False

        # Handle list
        if isinstance(value, list):
            # Interpret index
            try:
                if bit.endswith(map_char):
                    map_ret = True
                    bit = bit[:-len(map_char)]
                if ':' in bit:
                    index = _str_to_slice(bit)
                else:
                    index = int(bit)
            except (ValueError, TypeError):
                raise IndexError(error_msg + 'bad sequence index')

            # Access index
            try:
                value = value[index]
            except IndexError:
                raise IndexError(error_msg + 'index does not exist')

        # Handle dict
        elif isinstance(value, dict):
            if bit == map_char:
                map_ret = True
                value_ = []
                for k, v in value.items():
                    v = v.copy()
                    v[dict_key_key] = v.get(dict_key_key, k)
                    value_.append(v)
                value = value_
            else:
                try:
                    value = value[bit]
                except KeyError:
                    raise KeyError(error_msg + 'no such key')

        # Handle mapping
        if map_ret:
            retval = []
            for n, val in enumerate(value):
                try:
                    retval.append(traverse(val, sep.join(remaining),
                                           traversed=traversed,
                                           sep=sep,
                                           map_char=map_char,
                                           dict_key_key=dict_key_key))
                except (KeyError, IndexError) as e:
                    raise IndexError(error_msg + f'failed on {n}') from e
            # TODO: Make retval parents a bit more sensible
            return as_traversable(retval,
                                  parent=parent,
                                  path=sep.join(chain(traversed, remaining)),
                                  sep=sep,
                                  map_char=map_char,
                                  dict_key_key=dict_key_key)

    if isinstance(value, (list, dict)):
        return as_traversable(value,
                              parent=parent,
                              path=sep.join(traversed),
                              sep=sep,
                              map_char=map_char,
                              dict_key_key=dict_key_key)
    return value


class _EZBase:

    def __init__(self, underlying, *,
                 parent: Optional[Union['EZJL', 'EZJD']] = None,
                 path: str = '',
                 sep: str = DEFAULT_SEP,
                 map_char: str = DEFAULT_MAP,
                 dict_key_key: str = DEFAULT_MAP_KEY):
        self._underlying = underlying
        self._parent = parent
        self._path = path
        self._sep = sep
        self._map_char = map_char
        self._dict_key_key = dict_key_key

    @property
    def parent(self):
        return self._parent

    @property
    def root(self):
        root = self
        while root.parent is not None:
            root = root.parent
        return root

    @property
    def path(self):
        return self._path

    @property
    def key(self):
        return self._path.rsplit(self._sep)[-1]

    def __iter__(self) -> Iterator[str]:
        return iter(self._underlying)

    def __getitem__(self, path) -> EZJsonValues:
        return traverse(self._underlying, path,
                        sep=self._sep,
                        map_char=self._map_char,
                        dict_key_key=self._dict_key_key)

    def get(self, path, default: EZJsonValues = None) -> EZJsonValues:
        try:
            return self[path]
        except (IndexError, KeyError):
            return default

    def __len__(self) -> int:
        return len(self._underlying)

    def __repr__(self) -> str:
        name = type(self).__name__
        sep = '\n' + ' ' * (len(name) + 1)
        blob = sep.join(pformat(self._underlying, compact=True).splitlines())
        return (f'{name}({blob},'
                f'{sep}path={self._path!r},'
                f'{sep}sep={self._sep},'
                f'{sep}map_char={self._map_char},'
                f'{sep}dict_key_key={self._dict_key_key})')

    def __eq__(self, other) -> bool:
        return (isinstance(other, type(self)) and
                self._underlying == other._underlying and
                self._parent == other._parent and
                self._path == other._path and
                self._sep == other._sep and
                self._map_char == other._map_char and
                self._dict_key_key == other._dict_key_key)


class EZJL(_EZBase, Sequence[EZJsonValues]):
    pass


class EZJD(_EZBase, Mapping[str, EZJsonValues]):
    pass


def as_traversable(value: Union[Dict[str, Any], List[Any]], *,
                   parent: Optional[Union[EZJL, EZJD]] = None,
                   path: str = '',
                   sep: str = DEFAULT_SEP,
                   map_char: str = DEFAULT_MAP,
                   dict_key_key: str = DEFAULT_MAP_KEY):
    if isinstance(value, list):
        cls = EZJL
    elif isinstance(value, dict):
        cls = EZJD
    else:
        raise ValueError(f'Bad type, unexpected {type(value).__name__}')
    return cls(value,
               parent=parent,
               path=path,
               sep=sep,
               map_char=map_char,
               dict_key_key=dict_key_key)
