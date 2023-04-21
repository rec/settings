from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union
import dataclasses as dc
import json
import os
import sys

File = Tuple[Union[Path, str]]
_NONE = object()


class Configs:
    def diff(self, other: Any):
        assert self.__class__ is other.__class__
        result = {}
        for f in dc.fields(self):
            s, o = getattr(self, f.name), getattr(other, f.name)
            if s != o:
                if isinstance(s, Configs):
                    assert isinstance(o, Configs)
                    o = s.diff(o)
                result[f.name] = o

        return result

    def copy_from(self, **kwargs):
        for k, v in kwargs.items():
            attr = getattr(self, k)
            if isinstance(attr, Configs):
                attr.copy_from(**v)
            else:
                setattr(self, k, v)

    def load(self, *files: File):
        for f in files:
            self.copy_from(_load(f))

    def load_from_environ(
        self,
        prefix: str,
        environ: Optional[Dict] = None,
        verbose: bool = True,
    ):
        if environ is None:
            environ = os.environ
        pre = prefix.strip('_').upper() + '_'
        items = sorted(environ.items())
        items = ((k, v) for k, v in items if k.startswith(pre))

        for k, v in items:
            attr_name = k[len(pre):].lower()
            splits = list(_split_address(v, attr_name))
            if len(splits) == 1:
                parent, attr = splits[0]
                str_val = getattr(parent, attr)
                val = _string_value(k, v, str_val)
                setattr(parent, attr, val)
            elif not verbose:
                continue
            elif not splits:
                print('No configs match', k, file=sys.err)
            else:
                print('More than one config matches', k, file=sys.err)


def _split_address(parent, key):
    if key in dir(parent):
        yield parent, key
    else:
        for k in dir(parent):
            if k.startswith(key + '_'):
                k = key[len(key) + 1:]
                new_parent = getattr(parent, k)
                yield from _split_address(new_parent, k)


def _string_value(name, v, original_value):
    if original_value is None or isinstance(v, str):
        return v

    if isinstance(original_value, int):
        return int(v)

    if isinstance(original_value, float):
        return float(v)

    if isinstance(original_value, bool):
        if v.lower() in ('t', 'true'):
            return True
        if v.lower() in ('f', 'false'):
            return False
        raise ValueError(f'Cannot understand bool {name}={v}')

    if isinstance(original_value, Enum):
        return type(original_value)[v]

    return json.loads(v)


def _load(p):
    if p.suffix == '.json':
        return json.loads(p.read_text())

    if p.suffix == '.toml':
        try:
            import tomllib
            return tomllib.loads(p.read_text())
        except ImportError:
            import tomlkit
            return tomlkit.loads(p.read_text())

    if p.suffix == '.yaml':
        import yaml
        return yaml.safe_load(p.read_text())

    raise ValueError(f'Do not understand {p.suffix=}')
