import re

from collections import defaultdict
from tempfile import NamedTemporaryFile

from geyser import config
from geyser.core.artifact import Artifact
from geyser.utils.cmd import call
from geyser.utils.logging import log
import geyser.utils.jsonutils as json


def _artifact(s, is_internal):
    match = re.search(r'(.+):(.+)', s)
    if match:
        organization = match.group(1)
        name = match.group(2)
        internal = is_internal(organization)
        return Artifact(organization, name, internal)
    else:
        raise ValueError(f'Unable to parse {s}')


def parse_modules():
    all_modules = json.load(config.analysis_modules_file)
    return [_artifact(m, lambda a: True) for m in all_modules]


def parse_levels(modules):
    all_levels = json.load(config.analysis_levels_file)
    is_internal = lambda a: a in [m.organization for m in modules]
    return {_artifact(k, is_internal): v for k, v in all_levels.items()}


def parse_dependencies(modules):
    is_internal = lambda a: a in [m.organization for m in modules]
    add_to_list = lambda a: (not config.internal_only) or (config.internal_only and a.internal)

    depends_on = defaultdict(set)
    depended_by = defaultdict(set)
    connections = set()
    inverse_connections = set()
    for f, t in json.load(config.analysis_dependencies_file):
        from_artifact = _artifact(f, is_internal)
        to_artifact = _artifact(t, is_internal)
        if add_to_list(from_artifact) and add_to_list(to_artifact):
            depends_on[from_artifact].add(to_artifact)
            depended_by[to_artifact].add(from_artifact)
            connections.add((from_artifact, to_artifact))
            inverse_connections.add((to_artifact, from_artifact))
    return depends_on, depended_by, connections, inverse_connections


def write_graph(t, project, nodes):
    with NamedTemporaryFile(mode='w') as f:
        f.write('digraph {\n')
        f.write('  bgcolor=transparent\n')
        f.write('  rankdir=LR\n')
        f.write('  margin=0.5\n')
        f.write('  node [ fontname=helvetica, color=dimgray, style=rounded, shape=box ]\n')
        f.write('\n')

        for n in set(sum(nodes, ())):
            if n.internal:
                f.write(f'  "{n}" [ fontname=helvetica, color=dimgray, style="rounded,filled", shape=box, fillcolor=darkseagreen ]\n')
            else:
                f.write(f'  "{n}" [ fontname=helvetica, color=dimgray, style="rounded,filled", shape=box, fillcolor=deepskyblue ]\n')
        f.write('\n')

        for k, v in nodes:
            f.write(f'  "{k}" -> "{v}" \n')
        f.write('}\n')
        f.flush()

        call(f'tred {f.name} | dot -Tsvg -o /analysis/{project}.{t}.normalized.svg')
        log.info(f'Rendered {project}.{t}.normalized.svg')
        call(f'dot -Tsvg {f.name} -o /analysis/{project}.{t}.full.svg')
        log.info(f'Rendered {project}.{t}.full.svg')
