import json

from geyser.core.artifact import Artifact


def load(file):
    with open(file, 'r') as f:
        return json.load(f)


def dump(obj, file):
    with open(file, 'w') as out:
        json.dump(obj, out, cls=JsonEncoder)


class JsonEncoder(json.JSONEncoder):
    # pylint: disable=arguments-differ,protected-access
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, Artifact):
            return str(obj)
        else:
            return json.JSONEncoder.default(self, obj)
