from geyser.report.common import parse_dependencies
from geyser.report.common import parse_levels
from geyser.report.common import parse_modules
from geyser.report.common import write_graph
from geyser.utils import color
from geyser.utils import symbol
from geyser.utils.logging import log


def _dependencies(dependencies, s, positive, negative):
    internal = [a for a in dependencies if a.internal]
    external = [a for a in dependencies if not a.internal]

    if dependencies:
        log.info(f'{positive} {color.bold(len(dependencies))} other projects ({color.bold(len(internal))} internal, {color.bold(len(external))} external)')
        for r in sorted(dependencies):
            log.info(f'  {s} {r}')
    else:
        log.info(f'{negative} any other project')


def _dependencies_per_level(dependencies, levels, s, positive, negative, reverse):
    if len(dependencies) > 0:
        references_per_level = {}
        for artifact in dependencies:
            if artifact in levels:
                level = int(levels[artifact])
                references_per_level.setdefault(level, set())
                references_per_level[level].add(artifact)
            else:
                log.warn(f'Missing level information for {artifact}')

        for level, refs in sorted(references_per_level.items(), reverse=reverse):
            log.info(f'{positive} {len(refs)} other projects in level {level}:')
            for artifact in sorted(refs):
                log.info(f'  {s} {artifact}')
    else:
        log.info(f'{negative} any other project')


def _flatten(traversed, artifact):
    all_artifacts = set(sum(traversed, ()))
    all_artifacts.discard(artifact)
    return all_artifacts


def _traverse_from(dependencies, artifact):
    def _visit(node):
        for dep in dependencies.get(node, set()):
            nodes.add((node, dep))
            _visit(dep)

    nodes = set()
    _visit(artifact)
    return nodes


def report(artifact, per_level):
    modules = parse_modules()
    levels = parse_levels(modules)
    depends_on, depended_by, connections, inverse_connections = parse_dependencies(modules)

    with log.tag(artifact):
        with log.tag('Depends on'):
            directly_depends_on = depends_on[artifact]
            transitive_dependency_traversal = _traverse_from(depends_on, artifact)
            transitively_depends_on = _flatten(transitive_dependency_traversal, artifact)

            _dependencies(directly_depends_on, symbol.direct_dependency, 'Directly depends on', 'Does not directly depend on')
            _dependencies(transitively_depends_on, symbol.transitive_dependency, 'Transitively depends on', 'Does not transitively depend on')
            write_graph('depends-on', artifact, transitive_dependency_traversal)
            if per_level:
                _dependencies_per_level(directly_depends_on, levels, symbol.direct_dependency, "Directly depends on", "Does not directly depend on", reverse=True)

        with log.tag('Depended on by'):
            directly_depended_by = depended_by[artifact]
            transitive_dependency_traversal = _traverse_from(depended_by, artifact)
            transitively_depended_by = _flatten(transitive_dependency_traversal, artifact)

            _dependencies(directly_depended_by, symbol.direct_reference, 'Directly depended on by', 'Is not directly depended on by')
            _dependencies(transitively_depended_by, symbol.transitive_reference, 'Transitively depended on by', 'Is not transitively depended on by')
            write_graph('depended-by', artifact, transitive_dependency_traversal)
            if per_level:
                _dependencies_per_level(directly_depended_by, levels, symbol.direct_reference, "Directly depended on by", "Is not directly depended on by", reverse=False)
