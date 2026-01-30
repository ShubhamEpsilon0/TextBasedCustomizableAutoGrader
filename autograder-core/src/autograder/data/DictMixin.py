from dataclasses import dataclass, fields

@dataclass
class DictMixin:
    def __iter__(self):
        for f in fields(self):
            alias = f.metadata.get("alias", f.name)
            yield alias, getattr(self, f.name)

    @classmethod
    def fromDict(cls, data: dict):
        init_kwargs = {}
        for f in fields(cls):
            alias = f.metadata.get("alias", f.name)
            if alias in data:
                init_kwargs[f.name] = data[alias]
        return cls(**init_kwargs)
