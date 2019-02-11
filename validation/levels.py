"""Validation error levels."""


class _Level:
    def __init__(self, name, level):
        self.name = str(name)
        self.level = int(level)

    def __lt__(self, other):
        return int(self) < int(other)

    def __gt__(self, other):
        return int(self) > int(other)

    def __ge__(self, other):
        return int(self) >= int(other)

    def __le__(self, other):
        return int(self) <= int(other)

    def __ne__(self, other):
        return int(self) != int(other)

    def __eq__(self, other):
        return int(self) == int(other)

    def __int__(self):
        return self.level

    def __repr__(self):
        return self.name

    def __hash__(self):
        return hash((self.name, self.level))

    @property
    def html_class(self):
        return self.name.lower()


class Levels:
    """Manage validation error levels."""

    CRITICAL = _Level("Critical", 10)
    ERROR = _Level("Error", 7)
    WARNING = _Level("Warning", 4)
    FORMATTING = _Level("Formatting", 2)
    levels = [CRITICAL, ERROR, WARNING, FORMATTING]
    names = {_.name.lower(): _ for _ in levels}
    numeric = {_.level: _ for _ in levels}

    @classmethod
    def all(cls):
        """Return all levels."""
        return sorted(cls.levels)

    @classmethod
    def filter(cls, objects, level):
        """Filter an iterable of objects with a label attribute.

        Return a list of objects for which the level attribute is greater or equal to level.
        """
        if level is None:
            return objects
        else:
            return [_ for _ in objects if cls.get(_.level) >= cls.get(level)]

    @classmethod
    def get(cls, identifier):
        """Return the _Level instance identified by identifier.

        identifier can be the name of the level, the numeric value of the level or the
        _Level instance.
        """
        if isinstance(identifier, _Level):
            return identifier
        elif isinstance(identifier, int):
            return cls.numeric[identifier]
        elif isinstance(identifier, str):
            return cls.names[identifier.lower()]
        raise ValueError("Level instance not recognised.")
