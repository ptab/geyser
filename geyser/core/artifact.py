from functools import total_ordering

from geyser import config
from geyser.utils.logging import log


@total_ordering
class Artifact:
    def __init__(self, organization, name, internal):
        self.organization = organization
        self.name = name
        self.internal = internal

    def __str__(self):
        return f'{self.organization}:{self.name}'

    def __repr__(self):
        return f'Artifact({str(self)})'

    def __eq__(self, other):
        if isinstance(other, Artifact):
            return self.organization == other.organization and self.name == other.name
        else:
            log.debug(f'Attempting to compare unrelated classes. self={self.__repr__()}, other={type(other).__name__}({other})')
            return False

    def __hash__(self):
        return hash((self.organization, self.name))

    def __lt__(self, other):
        return str(self) < str(other)
