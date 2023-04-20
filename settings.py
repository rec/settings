import dataclasses
from enum import Enum


class Settings:
    _attribs_set = None

    def __post_init__(self):
        self._attribs_set = set()

    def __setattr__(self, k, v):
        if self._attribs_set is None:
            super().__setattr__(k, v)
        else:
            previous = getattr(self, k)
            if isinstance(previous, Enum) and isinstance(v, str):
                v = type(previous)(v)

            self.__dict__[k] = v
            self._attribs_set.add(k)

    def changed_dict(self):
        result = {}
        try:
            d = self.asdict()
        except Exception:
            d = dataclasses.asdict(self)

        for k, v in d.items():
            if isinstance(v, Settings):
                d = v.asdict()
                if d:
                    result[k] = d
            elif k in self._attribs_set:
                result[k] = v

        return result

    def copy_from(self, **kwargs):
        for k, v in kwargs.items():
            attr = getattr(self, k)
            if isinstance(attr, Settings):
                attr.copy_from(**v)
            else:
                setattr(self, k, v)
