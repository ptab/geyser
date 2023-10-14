import statistics
from collections import defaultdict

from geyser.report.common import parse_dependencies
from geyser.report.common import parse_levels
from geyser.report.common import parse_modules
from geyser.report.common import write_graph
from geyser.utils import color
from geyser.utils import symbol
from geyser.utils.logging import log


def _couplers(dependencies, limit, level=None, reverse=True):
    total = len(dependencies)
    avg = statistics.mean([len(v) for v in dependencies.values()])
    median = statistics.median([len(v) for v in dependencies.values()])
    actual_limit = min(limit, total) if limit else total
    description = f'Level {color.bold(level)}' if level else 'Top couplers' if reverse else f'Bottom couplers'

    log.info(f'{description} ({total} projects, avg={avg:.0f}, median={median:.0f}):')

    for k in sorted(dependencies, key=lambda k: len(dependencies[k]), reverse=reverse)[:actual_limit]:
        log.info(f'  {symbol.transitive_reference} {k} depended on by {color.bold(len(dependencies[k]))} projects')


def _couplers_per_level(dependencies, levels, limit):
    references_per_level = {}

    for artifact, references in dependencies.items():
        level = levels[artifact]
        references_per_level.setdefault(level, {})
        references_per_level[level][artifact] = references

    projects_per_level = defaultdict(set)
    for artifact, level in levels.items():
        projects_per_level[level].add(artifact)

    for level in sorted(projects_per_level):
        if level in references_per_level:
            _couplers(references_per_level[level], limit, level)
        else:
            project_count = len(projects_per_level[level])
            log.info(f'Level {level} ({project_count} projects): no references to any other projects')


def report(limit):
    modules = parse_modules()
    levels = parse_levels(modules)
    depends_on, depended_by, connections, inverse_connections = parse_dependencies(modules)

    with log.tag("Repository"):
        with log.tag("Top couplers"):
            _couplers(depended_by, limit, reverse=True)
        with log.tag("Bottom couplers"):
            _couplers(depended_by, limit, reverse=False)
        with log.tag("Couplers"):
            _couplers_per_level(depended_by, levels, limit)

        with log.tag("Dependency graphs"):
            write_graph('depends-on', 'all', connections)
            write_graph('depended-by', 'all', inverse_connections)

        with log.tag("Unused modules"):
            unused = [m for m in modules if m not in depended_by]
            if len(unused) > 0:
                log.warn(f'Found {color.bold(len(unused))} modules that are not depended on by any other project:')
                for u in sorted(unused):
                    log.warn(f'  {symbol.unused} {u}')
            else:
                log.info(f'Found no unused modules')
